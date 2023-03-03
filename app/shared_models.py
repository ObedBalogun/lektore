from django.db import models
from django_countries.fields import CountryField
from app.commons import GENDER
from django.contrib.auth.models import User

USER_ROLES = (('tutor', 'Tutor'), ('student', 'Student'))


class Timestamp(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CommonUserDetails(models.Model):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    postal_code = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    nationality = CountryField(blank=True)
    gender = models.CharField(max_length=15, choices=GENDER, blank=True, null=True)
    profile_picture = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


class UserVerificationModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=80, null=True, blank=True)
    otp_is_verified = models.BooleanField(blank=False, default=False)
    counter = models.IntegerField(default=0, blank=False)  # For non-timed otp Verification

    def __str__(self):
        return str(self.email)