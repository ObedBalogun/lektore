from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from app.services import SearchBarService, AzureStorageService
from app.utils.utils import ResponseManager


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
