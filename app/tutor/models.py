from django.contrib.auth.models import User
from django.db import models
from app.commons import EDUCATIONAL_QUALIFICATIONS

from app.shared_models import CommonUserDetails, Timestamp


class TutorProfile(CommonUserDetails, Timestamp):
    tutor_id = models.CharField(max_length=10, unique=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="tutor_profile")
    is_verified = models.BooleanField(default=False)
    is_qualified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class EducationalQualification(Timestamp):
    tutor = models.OneToOneField(TutorProfile, on_delete=models.CASCADE, related_name="educational_qualifications")
    highest_qualification = models.CharField(max_length=100, choices=EDUCATIONAL_QUALIFICATIONS)
    previous_age_group = models.CharField(max_length=100, blank=True, null=True,
                                          verbose_name="Previous Age Group Taught")
    current_age_group = models.CharField(max_length=100, blank=True, null=True,
                                         verbose_name="Current Age Group Able to Teach")
    teaching_experience = models.TextField(blank=True, null=True)
    subjects_taught = models.TextField(blank=True, null=True)
    qualified = models.BooleanField(default=False)
    pending_qualifications = models.CharField(max_length=255, blank=True, null=True, default="", verbose_name="Pending Qualifications")
    remote_teaching = models.BooleanField(default=False)
    intro_video = models.CharField(max_length=255, blank=True, null=True)
    tutor_resume = models.CharField(max_length=255, blank=True, null=True)
    certification_list = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.tutor.user.username
