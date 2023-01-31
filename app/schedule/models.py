from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    is_available = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    schedule_type = models.CharField(max_length=100, choices=(("group", "Group"), ("one_on_one", "One on One")),
                                     blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Availability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    monday = ArrayField(models.CharField(max_length=20), default=list)
    tuesday = ArrayField(models.CharField(max_length=20), default=list)
    wednesday = ArrayField(models.CharField(max_length=20), default=list)
    thursday = ArrayField(models.CharField(max_length=20), default=list)
    friday = ArrayField(models.CharField(max_length=20), default=list)
    saturday = ArrayField(models.CharField(max_length=20), default=list)
    sunday = ArrayField(models.CharField(max_length=20), default=list)

    def __str__(self):
        return self.user.username
