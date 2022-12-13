from typing import Type

from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from app.Tutee.models import TuteeProfile
from app.Tutor.models import TutorProfile
from app.submodels import UserVerificationModel

from app.helpers import user_login, user_logout, generate_key
from decouple import config
import base64
import pyotp

from app.utils.utils import EmailManager
from lektore import settings


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


class OTPService:
    @classmethod
    def _generate_or_verify_timed_otp(cls, email, verify=False, user_otp=None):
        expiry_time = int(config("RESET_EXPIRY_TIME"))  # seconds
        if verify:
            try:
                verification_model = UserVerificationModel.objects.get(email=email)
            except UserVerificationModel.DoesNotExist:
                return dict(error="User does not exist")
        else:
            verification_model = UserVerificationModel.objects.get_or_create(
                email=email
            )
        keygen: str = generate_key(email)
        key = base64.b32encode(
            keygen.encode()
        )  # Key is generated
        otp = pyotp.TOTP(key, 4, interval=expiry_time)  # TOTP Model for OTP is created
        if verify:
            if otp.verify(user_otp):
                verification_model.otp_is_verified = True
                verification_model.save()
            return otp.verify(user_otp)
        return otp, expiry_time / 60, verification_model

    @classmethod
    def request_otp(cls, request, verified=False, user_email=None):
        authenticated_user = request.user
        username = authenticated_user.username
        if not verified:
            try:
                verification_model = UserVerificationModel.objects.get(email=authenticated_user.email)

            except UserVerificationModel.DoesNotExist:
                return dict(error="User not found")

        otp, expiry_time, verification_obj = cls._generate_or_verify_timed_otp(user_email)

        url = f"{settings.LEKTORE_URL}/verify-email?email={user_email}&otp={otp.at(verification_model.counter)}"
        email_template_name = "email_template/email_verfication.txt"
        domain = request.META["HTTP_HOST"]
        site_name = "Lektore"
        data = {
            "email": user_email,
            "domain": domain,
            "site_name": site_name,
            "user": authenticated_user.id,
            "url": url
        }
        email_body = render_to_string(email_template_name, data)
        subject = "Lektore Verification"
        email_data = {
            'email_subject': subject,
            'email_body': email_body,
            'to_email': user_email
        }

        EmailManager.send_email(email_data)
        return dict(success="Verification mail has been sent")

    @classmethod
    def verify_email_otp(cls, request, **kwargs):
        user_otp = kwargs.get("otp", request.GET.get("otp"))
        user_id = kwargs.get("user_id", request.GET.get("user_id"))
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return dict(error="User does not exist")
        verified = cls._generate_or_verify_timed_otp(user.email, verify=True, user_otp=user_otp)
        return dict(success="OTP verified successfully") if verified else dict(error="Invalid OTP")
