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

    @action(detail=False, methods=["post"], url_path="update-qualification")
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

    # @action(detail=False, methods=["post"], url_path="update-qualification")
    # def update_education(self, request):
    #     tutor = TutorProfile.objects.get(user=request.user)
    #     request_data = request.data.copy()
    #     request_data.update(tutor=tutor.id)
    #     serialized_data = EducationSerializer(data=request_data)
    #     if not serialized_data.is_valid():
    #         return ResponseManager.handle_response(
    #             errors=serialized_data.errors,
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     copy_data = serialized_data.data
    #     if intro_video := serialized_data.validated_data.get('intro_video', None):
    #         video_extensions = config("VIDEO_EXTENSIONS").split(',')
    #         file_name = intro_video.name
    #         file_extension = file_name.split(".")[-1]
    #         if file_extension.lower() not in video_extensions:
    #             return ResponseManager.handle_response(
    #                 errors=dict(error="Invalid file extension"),
    #                 message="Course was not created.",
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         container_name = config("AZURE_VIDEO_CONTAINER_NAME")
    #         upload_file = AzureStorageService.upload_file(intro_video, file_name, container_name,
    #                                                       tutor.tutor_id)
    #         copy_data.update({"intro_video": str(upload_file)})
    #
    #     response = EducationService.update_education(**copy_data)
    #     return ResponseManager.handle_response(
    #         data=response.get("data"),
    #         message=response.get("message"),
    #         status=status.HTTP_400_BAD_REQUEST
    #         if response.get("error", None)
    #         else status.HTTP_200_OK,
    #     )

    @action(detail=False, methods=["post"], url_path="update-resume")
    def upload_resume(self, request):
        tutor = TutorProfile.objects.get(user=request.user)
        resume = request.data.get("resume", None)
        certification_list = request.data.get("certification_list", None)
        if type(certification_list) != list:
            certification_list = [certification_list]
        certification_url_list = []
        if not resume:
            return ResponseManager.handle_response(
                errors=dict(error="Resume is required"),
                status=status.HTTP_400_BAD_REQUEST
            )
        if not certification_list:
            return ResponseManager.handle_response(
                errors=dict(error="Certification list is required"),
                status=status.HTTP_400_BAD_REQUEST
            )
        # upload resume
        file_name = resume.name
        file_extension = file_name.split(".")[-1]
        if file_extension.lower() not in ["pdf"]:
            return ResponseManager.handle_response(
                errors=dict(error="Invalid file extension"),
                status=status.HTTP_400_BAD_REQUEST
            )
        container_name = config("AZURE_PDF_CONTAINER_NAME")
        resume_url = AzureStorageService.upload_file(resume, file_name, container_name,
                                                     tutor.tutor_id)
        # upload certifications
        for certification in certification_list:
            file_name = certification.name
            file_extension = file_name.split(".")[-1]
            if file_extension.lower() not in ["pdf"]:
                return ResponseManager.handle_response(
                    errors=dict(error="Invalid file extension"),
                    status=status.HTTP_400_BAD_REQUEST
                )
            container_name = config("AZURE_PDF_CONTAINER_NAME")
            upload_file = AzureStorageService.upload_file(certification, file_name, container_name,
                                                          tutor.tutor_id)
            certification_url_list.append(str(upload_file))
        response = EducationService.upload_resume(tutor, resume_url, certification_url_list)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )
