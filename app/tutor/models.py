from django.contrib.auth.models import User
from django.db import models

from app.shared_models import CommonUserDetails, Timestamp


class TutorProfile(CommonUserDetails, Timestamp):
    tutor_id = models.CharField(max_length=10, unique=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    is_verified = models.BooleanField(default=False)
    is_qualified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
