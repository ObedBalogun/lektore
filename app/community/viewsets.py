from rest_framework import permissions, viewsets, serializers
from rest_framework import status
from rest_framework.decorators import action

from app.community.serializers import CommunityPostSerializer
from app.community.services import CommunityService
from app.serializers import inline_serializer
from app.utils.utils import ResponseManager


class CommunityPostViewSets(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="create-post")
    def create_post(self, request):
        serialized_data = CommunityPostSerializer(data=request.data)
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="Community post was not created.",
                status=status.HTTP_400_BAD_REQUEST
            )

        response = CommunityService.create_post(request, **serialized_data.data)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="appraise_post")
    def appraise_post(self, request):
        serialized_data = inline_serializer(
            fields={
                "post_id": serializers.UUIDField(),
                "appraisal_type": serializers.CharField(max_length=4),
            },
            data=request.data
        )
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="Invalid request",
                status=status.HTTP_400_BAD_REQUEST
            )

        response = CommunityService.appraise_post(request, **serialized_data.data)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="remove_appraisal")
    def remove_appraisal(self, request):
        serialized_data = inline_serializer(
            fields={
                "post_id": serializers.UUIDField(),
            },
            data=request.data
        )
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=serialized_data.errors,
                message="Invalid request",
                status=status.HTTP_400_BAD_REQUEST
            )

        response = CommunityService.remove_appraisal(request, **serialized_data.data)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="get-posts")
    def get_community_posts(self, request):
        response = CommunityService.get_community_posts(request)
        return ResponseManager.handle_response(
            data=response.get("data"),
            message=response.get("message"),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )
