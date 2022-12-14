from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action

from app.Course.models import Course
from app.Course.serializers import CourseSerializer
from app.Course.services import CourseService
from app.serializers import inline_serializer
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
        response = CourseService.create_course(**serialized_data.data)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="get-course")
    def get_course_by_id(self, request):
        course_code = request.GET.get("course_id")
        response = CourseService.get_course(course_code)
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
