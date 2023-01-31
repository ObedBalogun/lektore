from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_countries.fields import CountryField

from app.commons import EXPERIENCE, SERVICES
from app.shared_models import CommonUserDetails


class TuteeProfile(CommonUserDetails):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    experience_level = models.CharField(max_length=100, choices=EXPERIENCE, blank=True, null=True)
    service = ArrayField(models.CharField(max_length=100, choices=SERVICES), blank=True,
                         null=True, default=list)
    is_qualified = models.BooleanField(default=False)
    from_destination = CountryField(blank=True)
    to_destination = CountryField(blank=True)
