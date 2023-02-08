from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from app.serializers import UserSerializer, UserDetailsSerializer
from app.services import UserService, SearchBarService, AzureStorageService
from app.utils.utils import ResponseManager
from decouple import config
from rest_framework.parsers import MultiPartParser, FormParser


class UserRegistrationAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
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


class UserLogin(generics.GenericAPIView):
    def post(self, request, format=None):
        serialized_data = UserDetailsSerializer(data=request.data)
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="Incorrect user credentials", status=status.HTTP_400_BAD_REQUEST)

        response = UserService.app_user_login(self.request, **serialized_data.data)

        return ResponseManager.handle_response(
            message=response.get("message", None),
            errors=response.get("error", None),
            data=response.get("data", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )


class UserLogout(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        response = UserService.app_user_logout(request)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_204_NO_CONTENT,
        )


class SearchBar(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        query_param = request.GET.get("query_param")
        response = SearchBarService.query_database(query_param)
        return ResponseManager.handle_response(
            message=response.get("message", None),
            data=response.get("data", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )
