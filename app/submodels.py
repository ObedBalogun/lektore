from django.db import models
from django_countries.fields import CountryField
from app.commons import GENDER

USER_ROLES = (('tutor', 'Tutor'), ('student', 'Student'))


class CommonUserDetails(models.Model):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    nationality = CountryField(blank=True)
    gender = models.CharField(max_length=15, choices=GENDER, blank=True, null=True)
    profile_picture = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True
