from django.db import models
from django.contrib.auth.models import User

from app.tutee.models import TuteeProfile
from app.tutor.models import TutorProfile
from app.shared_models import Timestamp


class Course(Timestamp):
    course_name = models.CharField(max_length=255)
    course_id = models.CharField(max_length=25, unique=True)
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="tutor_courses")
    course_duration = models.FloatField(default=0, verbose_name="Course Duration in hours")
    course_category = models.CharField(max_length=50,
                                       choices=(('ielts', 'IELTS'), ('elocution', 'Elocution'), ('other', 'Other')))
    course_type = models.CharField(max_length=50, choices=(('live', 'Live'), ('other', 'Other')))

    course_rate = models.CharField(max_length=10, choices=(('hr', '/hr'), ('total', 'total')))
    course_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=19)
    course_description = models.TextField()
    course_overview = models.TextField()
    intro_video = models.URLField(verbose_name="Link to video")
    is_active = models.BooleanField(default=True)
    course_rating = models.IntegerField(default=0)
    class Meta:
        indexes = [
            models.Index(fields=['course_id']),
        ]

    def __str__(self):
        return self.course_name

    @property
    def course_completion_percentage(self):
        module_count = self.course_modules.count()
        course_modules = Module.objects.filter(course_id=self.course_id)
        completed_modules = len([
            module for module in course_modules if module.is_module_completed
        ])
        return(completed_modules/module_count)*100


class Module(Timestamp):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_modules")
    module_name = models.CharField(max_length=256)
    module_description = models.TextField()
    module_duration = models.FloatField(default=0)
    module_video = models.URLField(verbose_name="Link to module video",null=True)
    module_audio = models.URLField(verbose_name="Link to module audio",null=True)
    module_pdf = models.URLField(verbose_name="Link to module pdf")
    is_module_video_completed = models.BooleanField(default=False)
    is_module_audio_completed = models.BooleanField(default=False)
    is_module_pdf_completed = models.BooleanField(default=False)


    ####### IN CASE OF MIGRATION TO 5.0 #######
    # is_completed = models.GeneratedField(
    #     expression=F("is_module_video_completed") and F("is_module_audio_completed") and F("is_module_pdf_completed"),
    #     output_field=models.BooleanField(),
    #     db_persist=False
    # )

    def __str__(self):
        return self.module_name

    @property
    def is_module_completed(self):
        return self.is_module_video_completed and self.is_module_audio_completed and self.is_module_pdf_completed

class CourseOrder(Timestamp):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="course_orders")
    tutee = models.ForeignKey(User, on_delete=models.PROTECT)
    purchase_status = models.BooleanField(default=False)

    def __str__(self):
        return self.course.course_name

class CourseEnrollment(Timestamp):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="course_enrollment")
    tutee = models.ForeignKey(TuteeProfile, on_delete=models.PROTECT, related_name="tutee_course_class")
    module_completion_level = models.JSONField(verbose_name="completed tasks", null=True),
    completed_date = models.DateField(null=True, blank=True)
    last_seen = models.DateField(null=True, blank=True)

    def get_total_tutees(self):
        return self.tutee_set.all().count()

    def __str__(self):
        return self.course.course_name
