from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action

from app.services import AzureStorageService
from app.tutor.models import TutorProfile
from app.tutor.serializers import EducationSerializer
from app.tutor.services import EducationService, TutorService
from app.utils.utils import ResponseManager

from decouple import config


class TutorViewset(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="get-tutor")
    def get_tutor(self, request):
        tutor_id = request.GET.get("tutor_id", None)
        response = TutorService.get_tutor(tutor_id=tutor_id)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )
    @action(detail=False, methods=["post"], url_path="create-education")
    def create_education(self, request):
        tutor = TutorProfile.objects.get(user=request.user)
        request_data = request.data.copy()
        request_data.update(tutor=tutor.id)
        serialized_data = EducationSerializer(data=request_data)
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        copy_data = serialized_data.data
        if intro_video := serialized_data.validated_data.get('intro_video', None):
            video_extensions = config("VIDEO_EXTENSIONS").split(',')
            file_name = intro_video.name
            file_extension = file_name.split(".")[-1]
            if file_extension.lower() not in video_extensions:
                return ResponseManager.handle_response(
                    errors=dict(error="Invalid file extension"),
                    message="Course was not created.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            container_name = config("AZURE_VIDEO_CONTAINER_NAME")
            upload_file = AzureStorageService.upload_file(intro_video, file_name, container_name,
                                                          tutor.tutor_id)
            copy_data.update({"intro_video": str(upload_file)})

        response = EducationService.create_education(**copy_data)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )
