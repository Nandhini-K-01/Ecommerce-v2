from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)
from django.core.validators import RegexValidator, validate_email
from django.conf import settings
import uuid
from storeapp.models import SubscriptionPlan


phone_regex = RegexValidator(
    regex=r"^\d{10}",
    message="Phone number must be 10 digits only."
)


class UserManager(BaseUserManager):
    def create_user(self, phone_number, name, email):
        if not phone_number:
            raise ValueError("User must have a phone number")
        if not name:
            raise ValueError("User should provide a name")
        if not email:
            raise ValueError("User should provide a email")
        user = self.model(name=name, email=email, phone_number=phone_number)
        # user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number):
        user = self.create_user(phone_number)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    Custom User model.
    """
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=30, blank=False, null=False)
    phone_number = models.CharField(unique=True, max_length=10, null=False, blank=False, validators=[phone_regex])
    email = models.EmailField(blank=False, null=False, validators=[validate_email])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    subscription_type = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, null=True, blank=True)
    is_subscription_user = models.BooleanField(default=False)
    is_subscription_active = models.BooleanField(default=False)
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["name", "email"]

    objects = UserManager()

    def __str__(self):
        return self.phone_number


class OTPDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    phone_number = models.CharField(max_length=10, null=False, blank=False, validators=[phone_regex])
    otp = models.CharField(max_length=4)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.CharField(max_length=2, default=settings.MAX_OTP_TRY)
    otp_max_out = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)