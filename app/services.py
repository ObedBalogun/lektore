from typing import Type

from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from app.Tutee.models import TuteeProfile
from app.Tutor.models import TutorProfile
from app.helpers import user_login, user_logout


class UserService:
    @classmethod
    def create_user(cls, **kwargs) -> dict:
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        email = kwargs.get("email").lower()
        password = kwargs.get("password")
        role = kwargs.get("role")
        gender = kwargs.get("gender")
        nationality = kwargs.get("nationality")
        phone_number = kwargs.get("phone_number")
        try:
            user_exists = User.objects.filter(username__iexact=email).exists()
            if user_exists:
                return dict(
                    error="User already exists",
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                user = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email,
                                           password=password)
                user.set_password(password)
                user.save()
                if role == 'tutor':
                    app_user = TutorProfile.objects.create(user=user, phone_number=phone_number,
                                                           nationality=nationality, gender=gender)
                if role == 'tutee':
                    app_user = TuteeProfile.objects.create(user=user)
                return dict(data=email, message=f"{role} with email, {email} successfully created")

        except Exception as e:
            print(e)
            return dict(
                error="User already exists",
                status=status.HTTP_400_BAD_REQUEST
            )

    @classmethod
    def app_user_login(cls, request, **kwargs) -> dict:
        username = kwargs.get("username")
        password = kwargs.get("password")
        try:
            user = User.objects.get(username=username)
            _user = authenticate(username=username, password=password)
            if _user is not None:
                _login: Type[Token] = user_login(request, user)
                return dict(data=_login.key, message=f"User {username} successfully logged in")
            else:
                return dict(error=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return dict(error=f"User with username {username} not found")

    @classmethod
    def app_user_logout(cls, request):
        user_logout(request)
        return dict(message="User successfully logged out")
