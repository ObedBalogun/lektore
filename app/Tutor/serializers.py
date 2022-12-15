from rest_framework.serializers import ModelSerializer

from app.Tutor.models import TutorProfile
from app.serializers import TutorUserSerializer


class TutorSerializer(ModelSerializer):
    user = TutorUserSerializer()

    class Meta:
        model = TutorProfile
        exclude = ['id', 'created', 'updated']
