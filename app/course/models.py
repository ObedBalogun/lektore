from django.db import models
from app.tutor.models import TutorProfile
from app.shared_models import Timestamp


class Course(Timestamp):
    course_name = models.CharField(max_length=255)
    course_id = models.CharField(max_length=25, unique=True)
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    course_duration = models.FloatField(default=0)
    course_category = models.CharField(max_length=50)
    course_type = models.CharField(max_length=50, choices=(('live', 'Live'), ('other', 'Other')))

    course_rate = models.CharField(max_length=10, choices=(('hr', '/hr'), ('total', 'total')))
    course_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=19)
    course_description = models.TextField()
    course_overview = models.TextField()
    intro_video = models.URLField()
    is_active = models.BooleanField(default=True)
    course_rating = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['course_id']),
        ]

    def __str__(self):
        return self.course_name


class Module(Timestamp):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_modules")
    module_name = models.CharField(max_length=256)
    module_description = models.TextField()
    module_duration = models.FloatField(default=0)
    module_video = models.URLField(verbose_name="Link to module video", null=True)
    module_audio = models.URLField(verbose_name="Link to module audio", null=True)
    module_pdf = models.URLField(verbose_name="Link to module pdf")

    def __str__(self):
        return self.module_name
import uuid

from app.shared_models import Timestamp
from django.db import models
from django.contrib.auth.models import User

from app.tutee.models import TuteeProfile
from app.tutor.models import TutorProfile


class VideoRoom(Timestamp):
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=True)
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



