from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app.tutor.services import TutorService
from app.utils.utils import ResponseManager
import rest_framework.status as status


class TutorProfileView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        tutor_id = request.GET.get("tutor_id", None)
        response = TutorService.get_tutor(tutor_id=tutor_id)
        return ResponseManager.handle_response(
            errors=response.get("error", None),
            data=response.get("data", None),
            status=status.HTTP_400_BAD_REQUEST
            if response.get("error", None)
            else status.HTTP_200_OK,
        )
