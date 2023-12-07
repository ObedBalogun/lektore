from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action

from app.services import AzureStorageService
from app.tutee.services import TuteeService
from app.tutor.models import TutorProfile
from app.tutor.serializers import EducationSerializer
from app.tutor.services import EducationService, TutorService
from app.utils.utils import ResponseManager

from decouple import config


class TuteeViewset(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="get-tutees")
    def get_tutee(self, request):
        filter_params = request.GET.keys()
        filter_values = request.GET.values()
        filter_body = {param: value for param, value in zip(filter_params, filter_values)}
        response = TuteeService.get_tutee(**filter_body)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )


