from app.serializers import inline_serializer
from app.utils.utils import CustomResponseMixin, ResponseManager
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status, serializers
from .services import VideoService
class VideoConference(viewsets.ViewSet, CustomResponseMixin):
    permission_classes = [permissions.IsAuthenticated]
    @action(detail=False, methods=["post"], url_path="create-room")
    def create_room(self, request):
        serialized_data = inline_serializer(
            fields={
                "tutor_id":serializers.CharField(max_length=10),
                "room_description":serializers.CharField(max_length=10),
                "room_name":serializers.CharField(max_length=256)
            },
            data=request.data
        )
        if errors := self.validate_serializer(serialized_data):
            return errors

        response = VideoService.create_room(**serialized_data.data)
        return self.response(response)
    @action(detail=False, methods=["get"], url_path="get-room")
    def get_room(self, request):
        response = VideoService.get_room(request)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="update-room")
    def update_room(self, request):
        serialized_data = inline_serializer(
            fields={
                "tutee_list":serializers.ListSerializer(child=serializers.CharField(max_length=10)),
                "room_id":serializers.CharField(max_length=100),
            },
            data=request.data
        )
        if errors := self.validate_serializer(serialized_data):
            return errors
        response = VideoService.update_room(**serialized_data.data)
        return self.response(response)

