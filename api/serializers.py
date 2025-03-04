from rest_framework import serializers
from storeapp.models import Product, Category, Review, Cart, Cartitems, ProductImage, Profile, Order, OrderItem, SubscriptionPlan
from django.db import transaction
from django.contrib.auth import get_user_model
from otp_auth.utils import get_or_none
from otp_auth.serializers import UserSerializer

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "title", "slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "image"]


class ProductSerilaizer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child = serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only = True
    )

    # category field expects the primary key (UUID or ID) of existing category when creating or updating a product.
    # queryset=Category.objects.all() ensures the field only accepts valid category IDs from the Category table.
    # category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
      
    class Meta:
        model = Product
        fields = ["id", "name", "description", "slug", "inventory", "category", "old_price", "price", "images", "uploaded_images"] # uploaded_images field is responsible for uploading multiple images

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")
        product = Product.objects.create(**validated_data)
        for uploaded_image in uploaded_images:
            ProductImage.objects.create(product=product, image=uploaded_image)
        return product


class ProductReadSerializer(ProductSerilaizer):
    category = CategorySerializer(read_only=True)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "name", "description"]

    def create(self, validated_data):
        product_id = self.context["product"]
        return Review.objects.create(product_id = product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]

class CartItemSerializer(serializers.ModelSerializer):
    sub_total = serializers.SerializerMethodField()
    product = SimpleProductSerializer()

    class Meta:
        model = Cartitems
        fields = ["id", "cart", "product", "quantity", "sub_total"]

    def get_sub_total(self, obj):
        return obj.quantity * obj.product.price


class AddCartItemSerializer(serializers.ModelSerializer):
    # product_id = serializers.UUIDField()
    class Meta:
        model = Cartitems
        fields = ["id", "product", "quantity"]

    # the below commented code is to check if product id exists or not, it is used when we mention product_id instead of product in fields array,
    # but here in this case drf automatically handles this

    # def validate_product_id(self, value):
    #     if not Product.objects.filter(pk=value).exists():
    #         raise serializers.ValidationError("There is no product associated with the given ID")

    # the below save method is used to check whether the item is already present in cart, if it is add the quantity or else create one
    def save(self, **kwargs):
        cart = self.context["cart_id"]
        product = self.validated_data["product"]
        quantity = self.validated_data["quantity"]

        try:
            cartitem = Cartitems.objects.get(product=product, cart=cart)
            cartitem.quantity += quantity
            cartitem.save()
            self.instance = cartitem

        except:
            self.instance = Cartitems.objects.create(cart_id=cart, **self.validated_data)
        
        # print(self.instance)
        return self.instance
    
    # if we not assign the cartitems to self.instance in both try and except it will return the data we entered that is product and quantity
    # whereas in above case it will return id, product and updated quantity

    # in modelserializer def save method returns self.instance so self.instance is used above

class UpdateCartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = Cartitems
        fields = ["id", "product", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True) # without this line items field will return only all the ids
    total = serializers.SerializerMethodField(method_name="main_total")

    class Meta:
        model = Cart
        fields = ["id", "items", "total"]
    
    def main_total(self, cart: Cart): # cart: Cart => Ensures cart is expected to be an instance of the Cart model. (is called type annotation)
        items = cart.items.all()
        total = sum([item.quantity * item.product.price for item in items])
        return total


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    owner = UserSerializer()
    class Meta:
        model = Order
        fields = ["uuid", "placed_at", "pending_status", "owner", "items"]
        # depth = 2


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def save(self,**kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context["user_id"]
            order = Order.objects.create(owner_id=user_id)
            cart_items = Cartitems.objects.filter(cart=cart_id)
            order_items = [OrderItem(
                                    order=order, 
                                    product=item.product, 
                                    quantity=item.quantity
                                ) 
                        for item in cart_items]
            OrderItem.objects.bulk_create(order_items)
            # Cart.objects.filter(id=cart_id).delete()

        return order


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'name', 'bio', 'picture']
    

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'duration', 'price']