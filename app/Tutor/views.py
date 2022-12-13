from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class TutorProfileView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
