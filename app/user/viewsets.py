from rest_framework.decorators import action
from rest_framework import permissions, status, viewsets, serializers
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from app.serializers import UserSerializer, UserDetailsSerializer, inline_serializer
from app.services import OTPService, UserService, AzureStorageService
from app.utils.utils import ResponseManager, CustomResponseMixin

from decouple import config


class UserViewSet(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @action(detail=False, methods=["post"], url_path="register-user")
    def register_user(self, request):
        serialized_data = UserSerializer(data=request.data)
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="User was not created.",
                status=status.HTTP_400_BAD_REQUEST
            )

        copy_data = serialized_data.data
        if profile_picture := serialized_data.validated_data.get('profile_picture', None):
            image_extensions = config("IMAGE_EXTENSIONS").split(',')
            file_name = profile_picture.name
            file_extension = file_name.split(".")[-1]
            if file_extension.lower() not in image_extensions:
                return ResponseManager.handle_response(
                    errors=dict(error="Invalid file extension"),
                    message="User was not created.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            container_name = config("AZURE_IMAGE_CONTAINER_NAME")
            upload_file = AzureStorageService.upload_file(profile_picture, file_name, container_name,
                                                          copy_data['first_name'])
            copy_data.update({"profile_picture": str(upload_file)})

        response = UserService.create_user(request, **copy_data)

        return ResponseManager.handle_response(
            data=response.get("data"),
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["patch"], url_path="update-user")
    def update_user(self, request):
        serialized_data = inline_serializer(
            fields={
                "first_name": serializers.CharField(required=False),
                "last_name": serializers.CharField(required=False),
                "email": serializers.EmailField(required=False),
                "phone_number": serializers.CharField(required=False),
                "postal_code": serializers.CharField(required=False),
                "address": serializers.CharField(required=False),
                "profile_picture": serializers.ImageField(required=False),
                "nationality": serializers.CharField(required=False),
                "username": serializers.CharField(required=False),
                "role": serializers.CharField(required=False),
            },
            data=request.data)

        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="User was not updated.",
                status=status.HTTP_400_BAD_REQUEST
            )
        copy_data = serialized_data.data
        if profile_picture := serialized_data.validated_data.get('profile_picture', None):
            image_extensions = config("IMAGE_EXTENSIONS").split(',')
            file_name = profile_picture.name
            file_extension = file_name.split(".")[-1]
            if file_extension.lower() not in image_extensions:
                return ResponseManager.handle_response(
                    errors=dict(error="Invalid file extension"),
                    message="User was not updated.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            container_name = config("AZURE_IMAGE_CONTAINER_NAME")
            upload_file = AzureStorageService.upload_file(profile_picture, file_name, container_name,
                                                          copy_data['first_name'])
            copy_data.update({"profile_picture": str(upload_file)})

        response = UserService.update_user(**serialized_data.data)
        return ResponseManager.handle_response(
            data=response.get("data"),
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="user-login")
    def user_login(self, request):
        serialized_data = UserDetailsSerializer(data=request.data)
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="Incorrect user credentials", status=status.HTTP_400_BAD_REQUEST)
        response = UserService.app_user_login(self.request, **serialized_data.data)

        return ResponseManager.handle_response(
            data=response.get("data"),
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="user-logout")
    def user_logout(self, request):
        response = UserService.app_user_logout(request)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )


class OTPViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="request")
    def request_otp(self, request):
        response = OTPService.request_otp(request)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="verify-email")
    def verify_otp(self, request):
        _, response = OTPService.verify_email_otp(request)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("success", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )


class PasswordViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], url_path="request")
    def request_password_reset(self, request):
        serialized_data = inline_serializer(
            fields={
                "email": serializers.EmailField(),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors
        email = serialized_data.validated_data['email']
        response = OTPService.request_otp(request, initiator="reset", email=email)
        return self.response(response)

    @action(detail=False, methods=["post"], url_path="request-complete")
    def reset_password(self, request):
        serialized_data = inline_serializer(
            fields={
                "password": serializers.CharField(max_length=16, style={"input_type": "password"}),
                "otp": serializers.CharField(max_length=16),
                "email": serializers.EmailField(),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors
        response = UserService.reset_password(**serialized_data)

        return self.response(response)

    @action(detail=False, methods=["post"], url_path="request-complete", permissions=[permissions.IsAuthenticated])
    def change_password(self, request):
        serialized_data = inline_serializer(
            fields={
                "old_password": serializers.CharField(max_length=16, style={"input_type": "password"}),
                "new_password": serializers.CharField(max_length=16, style={"input_type": "password"}),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors
        response = UserService.change_password(**serialized_data)

        return self.response(response)


