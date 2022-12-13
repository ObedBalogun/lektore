from django.db import models


class Course(models.Model):
    course_name = models.CharField(max_length=255)
    course_duration = models.CharField(max_length=255,verbose_name="Course Duration in minutes")
    course_category = models.CharField(max_length=50,choices=(('live','Live'),('other','Other')))
    course_rate = models.CharField(max_length=10,choices=(('hr','/hr'),('total','total')))
    course_price = models.CharField(max_length=10)
    tutor = models.ForeignKey('Tutor.TutorProfile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)