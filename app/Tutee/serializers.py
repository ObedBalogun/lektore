from rest_framework import serializers

from app.Tutor.models import TutorProfile


class TutorDetails(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile

