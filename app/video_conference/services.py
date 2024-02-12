from app.tutee.models import TuteeProfile
from app.course.models import VideoRoom
from django.forms.models import model_to_dict
from django.db.models import Q
from rest_framework import status

from ..tutor.models import TutorProfile


class VideoService:
    @classmethod
    def get_room(cls, request):
        try:
            room = VideoRoom.objects.get(
                Q(room_name__iexact=request.GET.get("room_name")) | Q(room_id=request.GET.get("room_id")))
            return dict(data=model_to_dict(room), message="Room gotten")
        except VideoRoom.DoesNotExist:
            return dict(error="Room does not exist")

    @classmethod
    def create_room(cls, **kwargs):
        room_name = kwargs.get("room_name")
        room_description = kwargs.get("room_description")
        tutor_id = kwargs.get("tutor_id")

        try:
            tutor = TutorProfile.objects.get(tutor_id=tutor_id)
            video_room = VideoRoom.objects.create(room_name=room_name,
                                                  room_description=room_description, created_by=tutor)
            return dict(data=dict(
                room_id=video_room.room_id,
                room_name=video_room.room_description,
                room_description=video_room.room_description),
                success="Room created successfully", status=status.HTTP_201_CREATED)
        except Exception as e:
            return dict(error=str(e))

    @classmethod
    def update_room(cls, **kwargs):
        tutee_list = kwargs.get("tutee_list")
        room_id = kwargs.get("room_id")
        room = None
        try:
            room = VideoRoom.objects.get(room_id=room_id)
            for tutee in tutee_list:
                tutee_profile = TuteeProfile.objects.get(tutee_id=tutee)
                room.online_users.add(tutee_profile)
                room.save()
            return dict(data=dict(
                room_name=room.room_name,
                member_count=room.get_online_count()), success="Room updated")
        except VideoRoom.DoesNotExist:
            return dict(error="Room does not exist")
