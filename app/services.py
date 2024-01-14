from typing import Type

from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.forms import model_to_dict

from app.course.models import Course, Module
from app.serializers import CustomTokenObtainPairSerializer
from app.tutee.models import TuteeProfile
from app.tutor.models import TutorProfile
from app.shared_models import UserVerificationModel

from app.helpers import user_login, user_logout, generate_key, GenerateID
from decouple import config
import base64
import pyotp

from app.utils.utils import EmailManager

from azure.storage.blob import BlobServiceClient, ContentSettings


class UserService:
    @classmethod
    def create_user(cls, request, **kwargs) -> dict:
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        email = kwargs.get("email").lower()
        password = kwargs.get("password")
        role = kwargs.get("role")
        gender = kwargs.get("gender")
        nationality = kwargs.get("nationality")
        phone_number = kwargs.get("phone_number")
        profile_picture = kwargs.get("profile_picture")
        try:
            if user_exists := User.objects.filter(username=email).exists():
                return dict(
                    error="User already exists",
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email,
                                       password=password)
            user.set_password(password)
            user.save()
            app_user = ""
            if role == 'tutor':
                tutor_id = GenerateID.generate_id(TutorProfile, 5)
                app_user = TutorProfile.objects.create(user=user, tutor_id=tutor_id, phone_number=phone_number,
                                                       nationality=nationality, gender=gender,
                                                       profile_picture=profile_picture)
                app_user = model_to_dict(app_user, exclude=["id", "nationality", "current_country"])
            if role == 'tutee':
                tutee_id = GenerateID.generate_id(TuteeProfile, 5)
                app_user = TuteeProfile.objects.create(user=user, tutee_id=tutee_id, phone_number=phone_number,
                                                       nationality=nationality, gender=gender,
                                                       profile_picture=profile_picture)
                app_user = model_to_dict(app_user, exclude=["id", "nationality", "from_destination", "to_destination",
                                                            "current_country"])
            otp, _ = OTPService.request_otp(request=request, user=user)
            app_user.update({"otp": otp})
            return dict(data=app_user,
                        message=f"{role} with email, {email} successfully created")

        except Exception as e:
            print(e, "error")
            return dict(
                error=f"{e}",
                status=status.HTTP_400_BAD_REQUEST
            )

    @classmethod
    def update_user(cls, **kwargs):
        username = kwargs.get("username")
        role = kwargs.get("role")
        user = None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return dict(
                error="User does not exist",
                status=status.HTTP_400_BAD_REQUEST
            )

        if role == 'tutor':
            tutor_profile = user.tutor_profile

            for key, value in kwargs.items():
                if key != "username" and key != "role":
                    setattr(tutor_profile, key, value)
            tutor_profile.save()
        if role == 'tutee':
            tutee_profile = user.tutee_profile

            for key, value in kwargs.items():
                if key != "username" and key != "role":
                    setattr(tutee_profile, key, value)
            tutee_profile.save()
        return dict(data=model_to_dict(user, exclude=["id", "password"]),
                    message=f"{role} with username, {username} successfully updated",
                    )

    @classmethod
    def app_user_login(cls, request, **kwargs) -> dict:
        username = kwargs.get("username").lower()
        password = kwargs.get("password")
        user_id, role = None, None
        try:
            user = User.objects.get(username=username) if "@" not in username else User.objects.get(email=username)
            _user = authenticate(username=user.username, password=password)
            if _user is None:
                return dict(error=status.HTTP_401_UNAUTHORIZED, message="Invalid credentials")
            _login: Type[Token] = user_login(request, user,
                                             user_data=dict(username=username, password=password)).validated_data
            try:
                otp_is_verified = UserVerificationModel.objects.get(email=user.email).otp_is_verified
            except UserVerificationModel.DoesNotExist:
                otp_is_verified = False
            try:
                user_id = user.tutor_profile.tutor_id
            except TutorProfile.DoesNotExist:
                user_id = user.tutee_profile.tutee_id
            try:
                is_qualified = bool(user.tutor_profile.educational_qualifications)
            except Exception as e:
                is_qualified = False

            return dict(
                data={
                    "token": dict(refresh=_login["refresh"], access=_login["access"]),
                    "email_is_verified": otp_is_verified,
                    "profile_id": user_id,
                    "role": "tutor" if hasattr(user, "tutor_profile") else "tutee",
                    "is_qualified": is_qualified,
                },
                message=f"User {username} successfully logged in")
        except User.DoesNotExist:
            return dict(error=f"User with username {username} not found")

    @classmethod
    def app_user_logout(cls, request):
        user_logout(request)
        return dict(message="User successfully logged out")

    @classmethod
    def reset_password(cls, **kwargs) -> dict:
        password = kwargs.get("password")
        submitted_otp = kwargs.get("otp")
        email = kwargs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return dict(error="User does not exist")
        verified, err = OTPService.verify_email_otp(submitted_otp, user)
        if not verified:
            return err
        user.set_password(password)
        user.save()
        return dict(success="Password reset successfully!")

    @classmethod
    def change_password(cls, request, **kwargs) -> dict:
        user = request.user
        old_password = kwargs.get("old_password")
        if user.check_password(old_password):
            new_password = kwargs.get("new_password")
            user.set_password(new_password)
            user.save()
            return dict(success="Password changed successfully!")
        else:
            return dict(error="Password mismatch!")


class OTPService:
    @classmethod
    def _initiator(cls, obj, url=False, user=None, otp=None):
        env = config("ENV")
        # lektore_url = config("LEKTORE_URL_PROD") if env == "PROD" else config("LEKTORE_URL_TEST")
        host_machine = "http://localhost:3000" if env == "TEST" else "http://lektore.netlify.app"

        _dict_obj = {
            "reset": ("new_reset", "Password Reset"),
            "verification": ("new_verification", "Email Verification"),
        }
        try:
            _url_obj = {
                "reset": (f"{host_machine}/password-reset/{user.email}/{otp.now()}",
                          "email_template/password_reset.html"),
                "verification": (f"{host_machine}/email-verification/{user.email}/{otp.now()}",
                                 "email_template/email_verification.html"),
            }
            if url:
                return _url_obj.get(obj)
        except AttributeError:
            pass
        return _dict_obj.get(obj)

    @classmethod
    def _generate_or_verify_timed_otp(cls, user, initiator="verification", verify_otp=False, user_otp=None):
        expiry_time = int(config("RESET_EXPIRY_TIME"))  # seconds
        attr, _ = cls._initiator(initiator)
        if verify_otp:
            try:
                verification_model = UserVerificationModel.objects.get(email=user.email)
                # Ensure the OTP is for the verification purpose; email verification or password reset
                if not getattr(verification_model, attr) is True:
                    return False, dict(error='Invalid request!')

            except UserVerificationModel.DoesNotExist:
                return False, dict(error='Invalid request!')
        else:
            verification_model, _ = UserVerificationModel.objects.get_or_create(
                user=user
            )
        raw_token: str = generate_key(user.email)
        encoded_token = base64.b32encode(
            raw_token.encode()
        )  # Key is generated
        otp = pyotp.TOTP(encoded_token, 6, interval=expiry_time)  # TOTP Model for OTP is created
        if not verify_otp:
            setattr(verification_model, attr, True)
            verification_model.save()
            return otp.now(), expiry_time / 60, verification_model
        else:
            if otp.verify(user_otp):
                setattr(verification_model, attr, False)
                verification_model.save()
            return otp.verify(user_otp), dict(error="Invalid OTP")

    @classmethod
    def request_otp(cls, request, initiator='verification', user=None, email=None):
        email = email or request.query_params.get('email')
        if not user:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return dict(error='User not found!')

        otp, expiry_time, _ = cls._generate_or_verify_timed_otp(user, initiator)

        # This Url leads to an external web application for verification
        url, email_template_name = cls._initiator(initiator, True, user, otp)
        _, email_subject = cls._initiator(initiator)
        domain = request.META["HTTP_HOST"] if request else "lektore.com"
        site_name = "Lektore"
        data = {
            "email": user.email,
            "domain": domain,
            "site_name": site_name,
            "user": user.id,
            "OTP": url
        }
        email_body = render_to_string(email_template_name, data)
        email_data = {
            'email_subject': email_subject,
            'email_body': email_body,
            'to_email': user.email
        }
        # email_user(**data)
        return otp, dict(success=f"{email_subject} OTP has been sent", data=url)

    @classmethod
    def verify_email_otp(cls, request, user=None, **kwargs):
        user_otp = kwargs.get("otp", request.data.get("otp"))
        email = kwargs.get("email", request.data.get("email"))
        if not user:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return dict(error="User does not exist")
        verified, error_response = cls._generate_or_verify_timed_otp(user, verify_otp=True, user_otp=user_otp)
        return (True, dict(success="OTP verified successfully")) if verified else (False, error_response)


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


class AzureStorageService:
    connect_str = config('AZURE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    @classmethod
    def list_containers(cls):
        return cls.blob_service_client.list_containers()

    @classmethod
    def create_container(cls, container_name, container_type):
        container_name = container_name.lower()
        if container_type == "pdf":
            container_name = f"{container_name}-pdf"
        elif container_type == "image":
            container_name = f"{container_name}-images"
        elif container_type == "video":
            container_name = f"{container_name}-videos"
        container_client = cls.blob_service_client.create_container(container_name)
        return "Container created successfully"

    @classmethod
    def upload_file(cls, file, file_name, container_name, username):
        blob_client = cls.blob_service_client.get_blob_client(container=container_name, blob=f'{username}/{file_name}')
        content_settings = ContentSettings(content_type=file.content_type)
        blob_client.upload_blob(file, content_settings=content_settings)
        return blob_client.url

    @classmethod
    def download_file(cls, file_name, container_name, container_type):
        container_name = container_name.lower()
        blob_client = cls.blob_service_client.get_container_client(container=container_name)
        return blob_client.download_blob(blob=file_name)

    @classmethod
    def delete_file(cls, file_name, container_name, container_type):
        container_name = container_name.lower()
        if container_type == "pdf":
            container_name = f"{container_name}-pdf"
        elif container_type == "image":
            container_name = f"{container_name}-images"
        elif container_type == "video":
            container_name = f"{container_name}-videos"
        blob_client = cls.blob_service_client.get_blob_client(container=container_name, blob=file_name)
        blob_client.delete_blob()
        return "File deleted successfully"
