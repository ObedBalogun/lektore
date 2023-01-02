from typing import Type

from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.forms import model_to_dict

from app.Course.models import Course, Module
from app.Tutee.models import TuteeProfile
from app.Tutor.models import TutorProfile
from app.submodels import UserVerificationModel

from app.helpers import user_login, user_logout, generate_key, GenerateID
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
                app_user = ""
                if role == 'tutor':
                    tutor_id = GenerateID.generate_id(TutorProfile, 5)
                    app_user = TutorProfile.objects.create(user=user, tutor_id=tutor_id, phone_number=phone_number,
                                                           nationality=nationality, gender=gender)
                if role == 'tutee':
                    tutee_id = GenerateID.generate_id(TuteeProfile, 5)
                    app_user = TuteeProfile.objects.create(user=user)
                return dict(data=model_to_dict(app_user, exclude=["nationality", "id"]),
                            message=f"{role} with email, {email} successfully created")

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
            if _user is None:
                return dict(error=status.HTTP_401_UNAUTHORIZED)
            _login: Type[Token] = user_login(request, user)
            try:
                otp_is_verified = UserVerificationModel.objects.get(email=username).otp_is_verified
            except UserVerificationModel.DoesNotExist:
                otp_is_verified = False
            return dict(data={"token": _login.key, "email_is_verified": otp_is_verified},
                        message=f"User {username} successfully logged in")
        except User.DoesNotExist:
            return dict(error=f"User with username {username} not found")

    @classmethod
    def app_user_logout(cls, request):
        user_logout(request)
        return dict(message="User successfully logged out")


class OTPService:
    @classmethod
    def _generate_or_verify_timed_otp(cls, user, email, verify_otp=False, user_otp=None):
        expiry_time = int(config("RESET_EXPIRY_TIME"))  # seconds
        if verify_otp:
            try:
                verification_model = UserVerificationModel.objects.get(email=email)
            except UserVerificationModel.DoesNotExist:
                return dict(error="User does not exist")
        else:
            verification_model, _ = UserVerificationModel.objects.get_or_create(
                user=user,
                email=email,
            )
        raw_token: str = generate_key(email)
        encoded_token = base64.b32encode(
            raw_token.encode()
        )  # Key is generated
        otp = pyotp.TOTP(encoded_token, 4, interval=expiry_time)  # TOTP Model for OTP is created

        if not verify_otp:
            return otp, expiry_time / 60, verification_model
        if otp.verify(user_otp):
            verification_model.otp_is_verified = True
            verification_model.save()
            return otp.verify(user_otp)

    @classmethod
    def request_otp(cls, request):
        env = config("ENV")
        lektore_url = config("LEKTORE_URL_PROD") if env == "PROD" else config("LEKTORE_URL_TEST")

        authenticated_user = request.user
        user_email = authenticated_user.email

        otp, expiry_time, verification_obj = cls._generate_or_verify_timed_otp(authenticated_user, user_email)

        url = f"{lektore_url}/verify-email?email={authenticated_user.email}&otp={otp.now()}"
        email_template_name = "email_template/email_verification.txt"
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
        return dict(message="Verification mail has been sent")

    @classmethod
    def verify_email_otp(cls, request, **kwargs):
        user_otp = kwargs.get("otp", request.GET.get("otp"))
        email = kwargs.get("email", request.GET.get("email"))
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return dict(error="User does not exist")
        verified = cls._generate_or_verify_timed_otp(user, user.email, verify_otp=True, user_otp=user_otp)
        return dict(success="OTP verified successfully") if verified else dict(error="Invalid OTP")


class SearchBarService:
    @classmethod
    def query_database(cls, search_param) -> dict:
        search_models = [TutorProfile, TuteeProfile, Course, Module]
        result_dict = {model.__name__: cls._search(model, search_param) for model in search_models}
        if list(result_dict.values()).count([]) == len(search_models):
            return dict(data={}, message=f"No results found for {search_param}")
        return dict(data=result_dict, message="Search results")

    @classmethod
    def _search(cls, model, search_param) -> list:
        result_list = []
        query_set = model.objects.all()
        for _object in query_set:
            query_fields = [_object.__dict__.values()]
            for field in query_fields:
                if search_param.lower() in str(field).lower():
                    result_list.append(model_to_dict(_object, exclude=["id", "nationality"]))
                    break
        return result_list
