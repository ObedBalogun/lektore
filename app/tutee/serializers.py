from rest_framework import serializers

from app.tutor.models import TutorProfile


class TutorDetails(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile

