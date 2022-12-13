from django.urls import path

from app.views import UserRegistrationAPIView, UserLogin, UserLogout

urlpatterns = [
    path('register-user/', UserRegistrationAPIView.as_view()),
    path('user-login/', UserLogin.as_view()),
    path('user-logout/', UserLogout.as_view())
]
