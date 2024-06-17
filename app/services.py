from datetime import datetime, timedelta
from typing import Type

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.forms import model_to_dict

from app.course.models import Course, Module
from app.tutee.models import TuteeProfile, TuteeService
from app.tutor.models import TutorProfile
from app.shared_models import UserVerificationModel, EmailVerification

from app.helpers import user_login, user_logout, generate_key, GenerateID
from datetime import timezone
from decouple import config
import base64
import pyotp


from azure.storage.blob import BlobServiceClient, ContentSettings,generate_blob_sas, BlobSasPermissions

from app.utils.utils import EmailManager


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
                moving_from = kwargs.get("moving_from")
                moving_to = kwargs.get("moving_to")
                profession = kwargs.get("profession")
                years_of_experience = kwargs.get("years_of_experience")
                services = kwargs.get("services")
                tutee_id = GenerateID.generate_id(TuteeProfile, 5)

                app_user = TuteeProfile.objects.create(user=user, tutee_id=tutee_id, phone_number=phone_number,
                                                       nationality=nationality, gender=gender,
                                                       profile_picture=profile_picture, moving_to=moving_to, moving_from=moving_from,
                                                       years_of_experience=years_of_experience, profession=profession)

                try:
                    for service in services:
                        tutee_service = TuteeService.objects.get(service=service)
                        app_user.services.add(tutee_service)
                        app_user.save()
                except TuteeService.DoesNotExist:
                    return dict(error="Tutee service does not exist",message="Please select a valid service")

                app_user = dict(
                    phone_number=app_user.phone_number,
                    gender=app_user.gender,
                    profile_picture=app_user.profile_picture or None,
                    tutee_id=app_user.tutee_id,
                    user=app_user.user.pk,
                    experience_level=app_user.experience_level,
                    service=[service.service for service in app_user.services.all()],
                    is_qualified=app_user.is_qualified)
            otp, _ = OTPService.get_user_otp(request=request, user_email=user.email)
            app_user.update({"otp": otp})
            return dict(data=app_user,
                        message=f"{role} with email, {email} successfully created", status=status.HTTP_201_CREATED)

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

    @staticmethod
    def generate_otp(user_email):
        otp_expiry_time = int(config("RESET_EXPIRY_TIME"))  # in minutes
        generated_token: str = generate_key(user_email)
        encoded_token = base64.b32decode(generated_token.encode())
        otp = pyotp.TOTP(encoded_token, 6, interval=otp_expiry_time)
        return otp

    @classmethod
    def send_verification_mail(cls, request, user_email, email_template, otp):
        env = config("ENV")
        host_machine = "http://localhost:3000" if env == "TEST" else "http://lektore.com"
        domain = request.META["HTTP_HOST"] if request else "lektore.com"
        url = f"{host_machine}/email-verification/{user_email}/{otp}"
        data = {
            "email_subject": "Lektore Email Verification",
            "to_email": user_email,
            "domain": domain,
            "site_name": "Lektore",
            "url": url,
        }
        try:
            EmailManager.send_email(data, email_template)
        except Exception as e:
            print(e)

    @classmethod
    def get_user_otp(cls, request, user_email):
        template = "email_verification.html"
        try:
            user = User.objects.get(user__email=user_email)
            user_verification, created = EmailVerification.objects.get_or_create(user__email=user_email,
                                                                                 defaults={user: user})
            if created:
                otp = cls.generate_otp(user_email)
                cls.send_verification_mail(request, user_email, template, otp)
                return otp.now()
        except Exception as e:
            print(e)

    @classmethod
    def verify_otp(cls, user_email):
        try:
            user_verification_model = EmailVerification.objects.get(email=user_email)
            otp = cls.generate_otp(user_email)
            user_verification_model.verified = otp.verify(user_email)
            user_verification_model.save()
            return user_verification_model.verified
        except ObjectDoesNotExist:
            return False


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

        sas_token = cls.generate_blob_sas_token(container_name,f'{username}/{file_name}')
        return f"{blob_client.url}?{sas_token}"

    @classmethod
    def generate_blob_sas_token(cls, container_name, blob_name):
        expiry = datetime.now(timezone.utc) + timedelta(days=3650)
        return generate_user_delegation_sas(
            account_name=cls.blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=expiry
        )
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
