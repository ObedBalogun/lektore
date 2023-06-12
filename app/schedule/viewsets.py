from rest_framework import permissions, status, viewsets

from rest_framework.decorators import action
from rest_framework import serializers

from .serializers import ScheduleSerializer
from .services import ScheduleService

from app.utils.utils import ResponseManager
from ..serializers import inline_serializer


class ScheduleViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 50

    @action(detail=False, methods=["post"], url_path="create-schedule")
    def create_schedule(self, request):
        request_data = request.data
        request_data.update({'user': request.user.pk})
        serialized_data = ScheduleSerializer(data=request_data)
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        response = ScheduleService.create_schedule(**serialized_data.data)

        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="all-schedules")
    def fetch_schedule_by_user(self, request):
        schedule_id = request.GET.get("schedule_id", None)
        if not schedule_id:
            response = ScheduleService.get_schedule_by_user(request)
            return ResponseManager.paginate_list_response(response.get("data", None), request)
        else:
            response = ScheduleService.get_schedule_by_user(request, schedule_id)
            return ResponseManager.handle_response(
                data=response.get("data", None),
                errors=response.get("error", None),
                message=response.get("message", None),
                status=status.HTTP_400_BAD_REQUEST
                if response.get("error", None)
                else status.HTTP_200_OK
            )

    @action(detail=False, methods=["patch"], url_path="update-schedule")
    def update_schedule(self, request):
        serialized_data = inline_serializer(
            fields={
                "schedule_id": serializers.IntegerField(required=True, allow_null=False),
                "title": serializers.CharField(max_length=100, required=False),
                "start_time": serializers.DateTimeField(required=False),
                "end_time": serializers.DateTimeField(required=False),
                "is_available": serializers.BooleanField(required=False),
                "description": serializers.CharField(max_length=16, required=False),
            },
            data=request.data)
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        response = ScheduleService.update_schedule(**serialized_data.data)

        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=True, methods=["delete"], url_path="delete-schedule")
    def delete_schedule(self, request, pk):
        serialized_data = inline_serializer(
            fields={
                "pk": serializers.IntegerField(required=True, allow_null=False),
            },
            data={"pk": pk})
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        response = ScheduleService.delete_schedule(**serialized_data.data)

        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )


class AvailabilityViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    @action(detail=False, methods=["post"], url_path="create-availability")
    def create_availability(self, request):
        request_data = request.data
        serialized_data = inline_serializer(fields={
            "user": serializers.IntegerField(required=True, allow_null=False),
            "sunday": serializers.CharField(max_length=10, required=False),
            "monday": serializers.ListField(child=serializers.CharField(), required=False),
            "tuesday": serializers.ListField(child=serializers.CharField(), required=False),
            "wednesday": serializers.ListField(child=serializers.CharField(), required=False),
            "thursday": serializers.ListField(child=serializers.CharField(), required=False),
            "friday": serializers.ListField(child=serializers.CharField(), required=False),
        }, data=request_data)

        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        response = ScheduleService.create_availability(**serialized_data.data)

        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="check-availability")
    def check_availability(self, request):
        response = ScheduleService.get_availability(request)

        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST if response.get("error", None)
            else status.HTTP_200_OK,
            data=response.get("data", None)

        )

    @action(detail=False, methods=["get"], url_path="update-availability")
    def update_availability(self, request):
        request_data = request.data
        serialized_data = inline_serializer(fields={
            "user": serializers.IntegerField(required=True, allow_null=False),
            "sunday": serializers.CharField(max_length=10, required=False),
            "monday": serializers.ListField(child=serializers.CharField(), required=False),
            "tuesday": serializers.ListField(child=serializers.CharField(), required=False),
            "wednesday": serializers.ListField(child=serializers.CharField(), required=False),
            "thursday": serializers.ListField(child=serializers.CharField(), required=False),
            "friday": serializers.ListField(child=serializers.CharField(), required=False),
        }, data=request_data)

        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        response = ScheduleService.update_availability(**serialized_data.data)

        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )
