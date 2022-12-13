from django.urls import path
from rest_framework.routers import DefaultRouter

from app.views import UserRegistrationAPIView, UserLogin, UserLogout
from app.viewsets import OTPViewSet

router = DefaultRouter()

router.register(r"user-otp", OTPViewSet, basename="user-otp")

urlpatterns = [
    path('register-user/', UserRegistrationAPIView.as_view()),
    path('user-login/', UserLogin.as_view()),
    path('user-logout/', UserLogout.as_view())
]
