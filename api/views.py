import uuid
from rest_framework.decorators import action
from .serializers import (
    ProductSerilaizer, 
    CategorySerializer, 
    ReviewSerializer, 
    CartSerializer, 
    ProductReadSerializer, 
    CartItemSerializer, 
    AddCartItemSerializer, 
    UpdateCartItemSerializer, 
    ProfileSerializer, 
    OrderSerializer, 
    CreateOrderSerializer,
    SubscriptionPlanSerializer)
from storeapp.models import Product, Category, Review, Cart, Cartitems, Profile, Order, OrderItem, SubscriptionPlan
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from django.conf import settings
from rest_framework.response import Response
import razorpay
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from storeapp.constants import PAYMENT_STATUS_COMPLETE, PAYMENT_STATUS_FAILED
import json
from urllib.parse import parse_qs
from .tasks import send_mail_func
from django.http.response import HttpResponse

# Create your views here.


class ProductViewset(ModelViewSet):
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ["category", "old_price"]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["old_price"]
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return ProductReadSerializer
        return ProductSerilaizer

class ReviewViewset(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product=self.kwargs["product_pk"])
    
    # get_serializer_context(self) in ModelViewSet returns a dictionary that contains additional context to be supplied to the serializer
    def get_serializer_context(self):
        return {"product": self.kwargs["product_pk"]}


class CategoryViewset(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminUser]


class CartViewset(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewset(ModelViewSet):
    # queryset = Cartitems.objects.all()
    # serializer_class = CartItemSerializer
    http_method_names = ["get","post","patch","delete"]

    def get_queryset(self):
        return Cartitems.objects.filter(cart=self.kwargs["cart_pk"])
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}
    

class OrderViewset(ModelViewSet):
    # queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


    @action(detail=True, methods=["GET"]) # detail=True: This means the action is for a single instance of a model
    def payment(self, request, pk):
        order = self.get_object()
        amount = order.total_price * 100
        name = request.user.name
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": amount, "currency": "INR", "payment_capture":1, "notes":{"order_uuid": str(order.uuid)}}
        )
        order = Order.objects.get(uuid=order.uuid)
        order.provider_order_id = razorpay_order["id"]
        order.save()
        return render(
            request,
            "payment.html",
            {
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "amount": amount,
                "currency": "INR",
                "name": name,
                "email": request.user.email,
                "contact": request.user.phone_number,
                "order_id": razorpay_order["id"]
            },
        )

    @method_decorator(csrf_exempt)
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def confirmpayment(self, request):
        payload = request.body.decode("utf-8")
        signature_id = request.headers.get("X-Razorpay-Signature")
        # signature_id = request.META.get("HTTP_X_RAZORPAY_SIGNATURE") # other way to get signature_id

        if signature_id:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            verify_signature = client.utility.verify_webhook_signature(payload, signature_id, settings.RAZORPAY_WEBHOOK_SECRET) # returns boolean
            payment_data = json.loads(payload)
            provider_order_id = payment_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
            payment_id = payment_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
            event = payment_data.get("event")

            order = Order.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.signature_id = signature_id
            order.save()

            if verify_signature and event != "payment.failed":
                order.pending_status = PAYMENT_STATUS_COMPLETE
                order.save()
                return render(request, "payment_status.html", {"status": "SUCCESSFULL"})
            else:
                order.pending_status = PAYMENT_STATUS_FAILED
                order.save()
                return render(request, "payment_status.html", {"status": "FAILED"})

        else:
            parsed_body = parse_qs(payload)
            # print("parsed_body", parsed_body) # o/p: parsed_body {'razorpay_payment_id': ['pay_PspWBMCYKUkn5V'], 'razorpay_order_id': ['order_PspViLTLLNSWDC'], 'razorpay_signature': ['431ff48990bb1dadbddecfa1e5af0a373e71171378542b3317393f977a042b1e']}
            provider_order_id = parsed_body.get("razorpay_order_id")[0]
            order = Order.objects.get(provider_order_id=provider_order_id)
            if order.pending_status == "C":
                return render(request, "payment_status.html", {"status": "SUCCESSFULL"})
            order.payment_id = payment_id
            order.pending_status = PAYMENT_STATUS_FAILED
            order.save()
            return render(request, "payment_status.html", {"status": "FAILED"})


    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(owner=user)
    
    # def get_serializer_class(self):
    #     if self.request.method == "POST":
    #         return CreateOrderSerializer
    #     return OrderSerializer
    
    # def get_serializer_context(self):
    #     return {"user_id": self.request.user.uuid}
    
    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data, context={"user_id": request.user.uuid})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

# class ProfileViewset(ModelViewSet):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer


class SubscriptionViewset(ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminUser]


def send_mail_to_users(request):
    send_mail_func.delay()
    return HttpResponse("Email sent to the users")






