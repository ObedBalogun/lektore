from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action

from decouple import config
from rest_framework import status, serializers
from app.course.serializers import CourseSerializer
from app.course.services import CourseService
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
        if intro_video := serialized_data.validated_data['intro_video']:
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

    @action(detail=False, methods=["get"], url_path="get-course")
    def get_course_by_id(self, request):
        filter_params = request.GET.keys()
        filter_values = request.GET.values()
        filter_body = {param:value for param, value in zip(filter_params, filter_values)}
        response = CourseService.get_course(**filter_body)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )
    @action(detail=False, methods=["get"], url_path="filter-courses")
    def get_course_by_id(self, request):
        filter_params = request.GET.keys()
        filter_values = request.GET.values()
        filter_body = {param:value for param, value in zip(filter_params, filter_values)}
        response = CourseService.get_course(**filter_body)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="all-courses")
    def get_all_courses(self, request):
        response = CourseService.get_course()
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="get-course-by-tutor")
    def get_course_by_tutor(self, request):
        tutor_id = request.GET.get("tutor_id")
        response = CourseService.get_course_by_tutor(tutor_id)
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

    @action(detail=False, methods=["post"], url_path="create-course")
    def create_module(self, request):
        serialized_data = inline_serializer(
            fields={
                "course": CourseSerializer(),
                "module_name": serializers.CharField(max_length=256),
                "module_description": serializers.CharField(),
                "module_duration": serializers.FloatField(),
                "module_video": serializers.URLField(),
                "module_pdf": serializers.URLField()
            },
            data=request.data
        )

        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="Course was not created.",
                status=status.HTTP_400_BAD_REQUEST
            )
        response = CourseService.create_course(**serialized_data.data)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )
