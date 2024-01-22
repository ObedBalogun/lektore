from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField

from app.commons import EXPERIENCE, SERVICES
from app.course.models import Course, Module
from app.shared_models import CommonUserDetails, Timestamp


class TuteeProfile(CommonUserDetails):
    tutee_id = models.CharField(max_length=10, unique=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="tutee_profile")
    experience_level = models.CharField(max_length=100, choices=EXPERIENCE, blank=True, null=True)
    # service = ArrayField(models.CharField(max_length=100, choices=SERVICES), blank=True,
    #                      null=True, default=list)
    is_qualified = models.BooleanField(default=False)
    from_destination = CountryField(blank=True)
    to_destination = CountryField(blank=True)
    last_seen = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.tutee_id}"


class TuteeOrder(Timestamp):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="tutee_orders")
    tutee = models.ForeignKey(TuteeProfile, on_delete=models.PROTECT)
    purchase_status = models.BooleanField(default=False)

    def __str__(self):
        return self.course.course_name

class RegisteredTuteeCourse(Timestamp):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="registered_tutees")
    module = models.ForeignKey(Module, on_delete=models.PROTECT, related_name="tutee_course_modules")
    tutee = models.ForeignKey(TuteeProfile, on_delete=models.PROTECT, related_name="registered_courses")
    is_module_video_completed = models.BooleanField(default=False)
    is_module_audio_completed = models.BooleanField(default=False)
    is_module_pdf_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)



    ####### IN CASE OF MIGRATION TO 5.0 #######
    # is_completed = models.GeneratedField(
    #     expression=F("is_module_video_completed") and F("is_module_audio_completed") and F("is_module_pdf_completed"),
    #     output_field=models.BooleanField(),
    #     db_persist=False
    # )
    def __str__(self):
        return f"{self.course.course_id}-{self.tutee.tutee_id}"
    @property
    def is_completed(self):
        return self.is_module_video_completed and self.is_module_audio_completed and self.is_module_pdf_completed

    @property
    def course_completion_percentage(self):
        module_count = self.course.course_modules.count()
        course_modules = Module.objects.filter(course_id=self.course_id)
        completed_modules = len([
            module for module in course_modules if module.is_module_completed
        ])
        return (completed_modules / module_count) * 100
