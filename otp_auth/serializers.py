from rest_framework import serializers
from django.contrib.auth import get_user_model
import random
from datetime import timedelta
from django.utils import timezone
from .utils import send_otp
from .models import OTPDetails
from django.conf import settings



User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "name", "email", "phone_number"]
    

class OTPDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPDetails
        fields = ["uuid", "phone_number"]
    
    def create(self, validated_data):
        otp = random.randint(1000,9999)
        otp_expiry = timezone.now() + timedelta(minutes=10)
        phone_number = validated_data["phone_number"]
        num_exists = OTPDetails.objects.filter(phone_number=phone_number).order_by('-created_at').first()
        otp_max_out = num_exists.otp_max_out if num_exists else None
        if not num_exists:
            max_otp_try = settings.MAX_OTP_TRY
        else:
            max_otp_try = int(num_exists.max_otp_try) - 1
            if max_otp_try == -1 and timezone.now() < otp_max_out:
                raise serializers.ValidationError(
                    {"message": "Max attempt reached. Try after some time"}
                )
            elif max_otp_try == -1 and timezone.now() > otp_max_out:
                max_otp_try = settings.MAX_OTP_TRY
                otp_max_out = None
            elif max_otp_try == 0:
                otp_max_out = timezone.now() + timedelta(minutes=15)

        otp_details = OTPDetails(
            phone_number = phone_number,
            otp = otp,
            otp_expiry = otp_expiry,
            max_otp_try = max_otp_try,
            otp_max_out = otp_max_out
        )
        otp_details.save()
        # send_otp(otp_details.phone_number, otp)
        return otp_details


class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["is_subscription_user", "is_subscription_active", "subscription_start_date", "subscription_end_date"]

    
    def save(self, **kwargs):
        user = self.instance
        if self.validated_data["subscription_end_date"] >= timezone.now().date():
            user.is_subscription_user = True
            user.is_subscription_active = True
            super().save(**kwargs)
        
        else:
            raise serializers.ValidationError("Subscription end date must be greater than current date")