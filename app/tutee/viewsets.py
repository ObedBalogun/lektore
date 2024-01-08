from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework import serializers

from app.course.services import CourseService, ModuleService
from app.serializers import inline_serializer
from app.tutee.services import TuteeService

from app.utils.utils import ResponseManager,CustomResponseMixin

class TuteeViewset(viewsets.ViewSet, CustomResponseMixin):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="get-tutees")
    def get_tutee(self, request):
        filter_params = request.GET.keys()
        filter_values = request.GET.values()
        filter_body = dict(zip(filter_params, filter_values))
        response = TuteeService.get_tutee(**filter_body)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="get-courses")
    def tutee_courses(self, request):
        tutee_email = request.user
        response = TuteeService.get_tutee_courses(tutee_email)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="purchase-course")
    def purchase_course(self, request):
        serialized_data = inline_serializer(fields={
            "cart_items":serializers.DictField(child=serializers.DictField()),
            # "sum_total": serializers.DecimalField(decimal_places=2)

        },data=request.data)
        if errors := self.validate_serializer(serialized_data):
            return errors

        response = TuteeService.purchase_course(**serialized_data.data)
        return self.response(response)

    @action(detail=False, methods=["post"], url_path="update-module")
    def update_module(self, request):
        serialized_data = inline_serializer(
            fields={
                "tutee_id":serializers.CharField(max_length=100),
                "module_id":serializers.CharField(max_length=100),
                "is_module_video_completed":serializers.BooleanField(required=False,allow_null=True),
                "is_module_audio_completed":serializers.BooleanField(required=False,allow_null=True),
                "is_module_pdf_completed":serializers.BooleanField(required=False,allow_null=True),
            },
            data=request.data
        )
        if errors := self.validate_serializer(serialized_data):
            return errors
        response = TuteeService.update_course(**serialized_data.data)
        return self.response(response)