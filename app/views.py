from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from app.serializers import UserSerializer, UserDetailsSerializer
from app.services import UserService, SearchBarService
from app.utils.utils import ResponseManager


class UserRegistrationAPIView(APIView):

    def post(self, request, format=None):
        serialized_data = UserSerializer(data=request.data)
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="User was not created.",
                status=status.HTTP_400_BAD_REQUEST
            )

        response = UserService.create_user(**serialized_data.data)

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
            data=response.get("data", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_204_NO_CONTENT,
        )


class SearchBar(generics.GenericAPIView):
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
