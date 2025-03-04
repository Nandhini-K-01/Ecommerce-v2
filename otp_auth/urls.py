from rest_framework.routers import DefaultRouter
from .views import OTPDetailsView, validateOTPView, UserView, UserSubscriptionPlanView
from django.urls import path


urlpatterns = [
    path("user/", OTPDetailsView.as_view()),
    path("validate-otp/", validateOTPView.as_view()),
    path("create-user/", UserView.as_view()),
    path("subscription/update/", UserSubscriptionPlanView.as_view())
]

