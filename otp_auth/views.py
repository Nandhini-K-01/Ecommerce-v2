from rest_framework import viewsets, status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, OTPDetailsSerializer, SubscriptionUpdateSerializer
from rest_framework.decorators import action
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.response import Response
from .utils import send_otp, get_tokens_for_user, get_or_none
from django.shortcuts import get_object_or_404
from .models import OTPDetails
from storeapp.models import SubscriptionPlan
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class OTPDetailsView(APIView):
    def post(self, request):
        serializer = OTPDetailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "data": serializer.data,
                "msg": "OTP sent successfully"
            }
        )


class validateOTPView(APIView):
    def post(self, request):
        phone_num = request.data["phone_number"]
        otp = request.data["otp"]
        uuid = request.data["uuid"]

        instance = get_or_none(OTPDetails, uuid=uuid)
        if not instance:
            return Response({"msg": "Invalid detail"}, status=400)

        elif instance.otp==otp and timezone.now() < instance.otp_expiry:
            instance.is_verified = True
            instance.save()
        
        else:
            return Response({"msg": "OTP verification failed"})
        
        user = get_or_none(User, phone_number=phone_num)
        if user:
            serializer = UserSerializer(user)
            token = get_tokens_for_user(user)
            return Response(
                {
                    "msg": "OTP verified successfully",
                    "data": serializer.data,
                    "token": token
                }
            )
        return Response({"msg": "OTP verified successfully"})


class UserView(APIView):
    def post(self, request):
        phone_num = request.data["phone_number"]
        user = User.objects.filter(phone_number=phone_num)
        if user:
            return Response(
                {"msg": "User already exists"},
                status = 400
            )
        else:
            instance = OTPDetails.objects.filter(phone_number=phone_num, is_verified=True, created_at__gte = timezone.now()-timedelta(hours=24))
            if not instance:
                return Response(
                    {"msg": "Verify your mobile number first"},
                    status = 400
                )
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "data": serializer.data
                }
            )


class UserSubscriptionPlanView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        user = request.user
        serializer = SubscriptionUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Subscription updated successfully"})


