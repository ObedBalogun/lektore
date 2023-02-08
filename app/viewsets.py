from rest_framework import permissions, status, viewsets

from rest_framework.decorators import action

from app.services import OTPService
from app.utils.utils import ResponseManager


class OTPViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="request")
    def request_otp(self, request):
        response = OTPService.request_otp(request)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("message", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="verify-email")
    def verify_otp(self, request):
        response = OTPService.verify_email_otp(request)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            message=response.get("success", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK
        )
