from rest_framework import serializers

from app.tutor.models import TutorProfile, EducationalQualification
from app.serializers import TutorUserSerializer


class TutorSerializer(serializers.ModelSerializer):
    user = TutorUserSerializer()

    class Meta:
        model = TutorProfile
        exclude = ['id', 'created', 'updated']


class EducationSerializer(serializers.ModelSerializer):
    intro_video = serializers.FileField(required=False)

    class Meta:
        model = EducationalQualification
        exclude = ['id', 'created', 'updated']
