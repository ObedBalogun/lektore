from rest_framework import serializers


class CourseSerializer(serializers.Serializer):
    course_name = serializers.CharField(max_length=255)
    tutor_id = serializers.CharField()
    course_duration = serializers.FloatField()
    course_category = serializers.CharField(max_length=50)
    course_type = serializers.CharField(max_length=50)
    course_rate = serializers.CharField(max_length=10)
    course_price = serializers.CharField(max_length=10)
    course_description = serializers.CharField()
    course_goal = serializers.CharField()
    intro_video = serializers.FileField()