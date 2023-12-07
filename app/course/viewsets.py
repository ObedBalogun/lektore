from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action

from decouple import config
from rest_framework import status, serializers
from app.course.serializers import CourseSerializer
from app.course.services import CourseService, ModuleService
from app.serializers import inline_serializer
from app.services import AzureStorageService
from app.utils.utils import ResponseManager


class CourseViewSets(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="create-course")
    def create_course(self, request):
        serialized_data = CourseSerializer(data=request.data)

        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="Course was not created.",
                status=status.HTTP_400_BAD_REQUEST
            )
        copy_data = serialized_data.data
        if intro_video := serialized_data.validated_data.get('intro_video'):
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
                                                          copy_data['tutor_id'])
            copy_data.update({"intro_video": str(upload_file)})

        response = CourseService.create_course(**copy_data)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="all-courses")
    def get_all_courses(self, request):
        filter_params = request.GET.keys()
        filter_values = request.GET.values()
        filter_body = {param: value for param, value in zip(filter_params, filter_values)}
        response = CourseService.get_course(**filter_body)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="delete-course")
    def delete_course(self, request):
        course_code = request.GET.get("course_id")
        response = CourseService.delete_course(course_code)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="create-module")
    def create_module(self, request):
        serialized_data = inline_serializer(
            fields={
                "course_id": serializers.CharField(max_length=100),
                "module_name": serializers.CharField(max_length=256),
                "module_description": serializers.CharField(max_length=500),
                "module_duration": serializers.FloatField(min_value=0.00),
                "module_video": serializers.FileField(allow_null=True,required=False),
                "module_pdf": serializers.FileField(allow_null=False, required=True),
                "module_audio": serializers.FileField(allow_null=True,required=False)
            },
            data=request.data
        )

        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="Course was not created.",
                status=status.HTTP_400_BAD_REQUEST
            )
        copy_data = serialized_data.data

        if module_video := serialized_data.validated_data['module_video']:
            video_extensions = config("VIDEO_EXTENSIONS").split(',')
            file_name = module_video.name
            file_extension = file_name.split(".")[-1]
            if file_extension.lower() not in video_extensions:
                return ResponseManager.handle_response(
                    errors=dict(error="Invalid file extension"),
                    message="Module was not created.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            container_name = config("AZURE_VIDEO_CONTAINER_NAME")
            upload_file = AzureStorageService.upload_file(module_video, file_name, container_name,
                                                          copy_data['course_id'])
            copy_data.update({"module_video": str(upload_file)})
        if module_pdf := serialized_data.validated_data['module_pdf']:
            file_name = module_pdf.name
            file_extension = file_name.split(".")[-1]
            if file_extension.lower() != "pdf":
                return ResponseManager.handle_response(
                    errors=dict(error="Invalid file extension"),
                    message="Module was not created.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            container_name = config("AZURE_PDF_CONTAINER_NAME")
            upload_file = AzureStorageService.upload_file(module_pdf, file_name, container_name,
                                                          copy_data['course_id'])
            copy_data.update({"module_pdf": str(upload_file)})
        if module_audio := serialized_data.validated_data['module_audio']:
            audio_extensions = config("AUDIO_EXTENSIONS").split(',')
            file_name = module_audio.name
            file_extension = file_name.split(".")[-1]
            if file_extension.lower() not in audio_extensions:
                return ResponseManager.handle_response(
                    errors=dict(error="Invalid file extension"),
                    message="Module was not created.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            container_name = config("AZURE_AUDIO_CONTAINER_NAME")
            upload_file = AzureStorageService.upload_file(module_pdf, file_name, container_name,
                                                          copy_data['course_id'])
            copy_data.update({"module_audio": str(upload_file)})


        response = ModuleService.create_module(**copy_data)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )
