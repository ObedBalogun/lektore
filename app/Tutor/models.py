from django.contrib.auth.models import User
from django.db import models

from app.submodels import CommonUserDetails


class TutorProfile(CommonUserDetails):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    is_verified = models.BooleanField(default=False)
    is_qualified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username