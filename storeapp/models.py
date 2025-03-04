from django.db import models
import uuid
from django.conf import settings
from .constants import PAYMENT_STATUS_CHOICES, PAYMENT_STATUS_PENDING
from datetime import timedelta

# Create your models here.
        
class Category(models.Model):
    title = models.CharField(max_length=200) # by default max_length is 50
    category_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True) # the datatype of uuid is uuid in postgres and mariadb, in other case it is charfield
    slug = models.SlugField(default= None) # short label for something
    featured_product = models.OneToOneField('Product', on_delete=models.CASCADE, blank=True, null=True, related_name='featured_product')
    icon = models.CharField(max_length=100, default=None, blank = True, null=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name = "reviews")
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(default="description")
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.description
    

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    discount = models.BooleanField(default=False)
    image = models.ImageField(upload_to='img',  blank=True, null=True, default='')
    old_price = models.FloatField(default=100.00)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    slug = models.SlugField(default=None, blank=True, null=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    inventory = models.IntegerField()
    top_deal=models.BooleanField(default=False)
    flash_sales = models.BooleanField(default=False)
    

    @property # this decorator used to make methods behave like attributes so that we can access as product.price instead of product.price()
    def price(self):
        if self.discount:
            new_price = self.old_price - ((30/100)*self.old_price)
        else:
            new_price = self.old_price
        return new_price

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="img", default="", null=True, blank=True) # upload_to, it creates a img folder within the media root directory


class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class Cartitems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items") # related_name creates a link between cart and cartitems model i.e. items field will be automatically created in the cart model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cartitems')
    quantity = models.PositiveSmallIntegerField(default=0)


class Profile(models.Model):
    name = models.CharField(max_length=30)
    bio = models.TextField()
    picture = models.ImageField(upload_to ='img', blank=True, null=True)
    
    def __str__(self):
        return self.name


class Order(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    pending_status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    provider_order_id  = models.CharField(max_length=50, null=True, blank=True)
    payment_id  = models.CharField(max_length=50, null=True, blank=True)
    signature_id  = models.CharField(max_length=100, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, to_field="uuid")
    
    def __str__(self):
        return self.pending_status
    
    @property
    def total_price(self):
        order_items = self.items.all()
        total = sum([item.product.price * item.quantity for item in order_items])
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name = "items", to_field="uuid")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.product.name

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    duration = models.IntegerField(help_text="Duration in days")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

