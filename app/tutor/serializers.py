from rest_framework import serializers

from app.tutor.models import TutorProfile, EducationalQualification
from app.serializers import TutorUserSerializer


class TutorSerializer(serializers.ModelSerializer):
    user = TutorUserSerializer()

    class Meta:
        model = TutorProfile
        exclude = ['id', 'created', 'updated','current_country']


class EducationSerializer(serializers.ModelSerializer):
    resume = serializers.FileField(required=False)
    intro_video = serializers.FileField(required=False)
    certification_list = serializers.JSONField(required=False)

    class Meta:
        model = EducationalQualification
        exclude = ['id', 'created', 'updated']
