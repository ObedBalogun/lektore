import uuid

from app.shared_models import Timestamp
from django.db import models
from django.contrib.auth.models import User

from app.tutee.models import TuteeProfile
from app.tutor.models import TutorProfile


class VideoRoom(Timestamp):
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_name = models.CharField(max_length=128)
    room_description = models.CharField(max_length=200)
    online_users = models.ManyToManyField(TuteeProfile, blank=True)
    created_by = models.ForeignKey(TutorProfile, related_name="tutor_rooms", null=True, blank=True, on_delete=models.CASCADE)
    duration = models.DateTimeField(null=True)

    def get_online_count(self):
        return self.online_users.count()

    def join(self, user):
        self.online_users.add(user)
        self.save()

    def leave(self, user):
        self.online_users.remove(user)
        self.save()

    def __str__(self):
        return f"{self.created_by} ({self.room_name})"
