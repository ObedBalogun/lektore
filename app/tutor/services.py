from datetime import datetime

from app.course.models import CourseEnrollment, Course
from app.schedule.models import Schedule
from app.tutor.models import TutorProfile, EducationalQualification
from django.forms import model_to_dict

from app.tutor.serializers import TutorSerializer
from app.wallet.models import Wallet


class TutorService:
    @classmethod
    def get_tutor(cls, **kwargs) -> dict:
        tutor_id = kwargs.get("tutor_id")
        if not tutor_id:
            tutors = TutorProfile.objects.all()
            serialized_data = TutorSerializer(tutors, many=True)
            return dict(message="All tutors retrieved successfully",
                        data=serialized_data.data)
        try:
            tutor = TutorProfile.objects.get(tutor_id=tutor_id)
            serialized_data = TutorSerializer(tutor)
            return dict(data=serialized_data.data)
        except TutorProfile.DoesNotExist:
            return dict(error="Tutor does not exist")


class EducationService:
    @classmethod
    def create_education(cls, **kwargs):
        tutor_profile = TutorProfile.objects.get(id=kwargs.get("tutor"))
        kwargs.pop("tutor")
        try:
            if education := EducationalQualification.objects.get(tutor=tutor_profile):
                return dict(error="Qualification already exists for user")
        except EducationalQualification.DoesNotExist:
            education = EducationalQualification.objects.create(
                tutor=tutor_profile,
                **kwargs
            )
            return dict(message="Education created successfully",
                        data=model_to_dict(education, exclude=["id"]))

    @classmethod
    def update_education(cls, **kwargs):
        tutor_profile = TutorProfile.objects.get(id=kwargs.get("tutor"))
        kwargs.pop("tutor")
        try:
            if education := EducationalQualification.objects.get(tutor=tutor_profile):
                education = EducationalQualification.objects.update(
                    tutor=tutor_profile,
                    **kwargs
                )
                return dict(message="Education updated successfully",
                            data=model_to_dict(education, exclude=["id"]))
        except EducationalQualification.DoesNotExist:
            return dict(error="Qualification does not exist for user")

    @classmethod
    def upload_resume(cls, tutor, resume_url, certification_list):
        try:
            if education := EducationalQualification.objects.get(tutor=tutor):
                education.resume = resume_url
                education.certification_list = certification_list
                education.save()
                return dict(message="Resume uploaded successfully",
                            data=model_to_dict(education, exclude=["id"]))
        except EducationalQualification.DoesNotExist:
            return dict(error="Qualification does not exist for user")

    @classmethod
    def dashboard(cls, request):
        tutor = TutorProfile.objects.get(user=request.user)
        schedule = Schedule.objects.filter(user=request.user, start_time__gte=datetime.now()).count()
        courses = tutor.tutor_courses.filter(is_active=True).count()
        total_earnings = Wallet.objects.filter(user=request.user).balance
        tutor_courses = Course.objects.filter(tutor=tutor)
        total_students = sum(
            course.course_enrollment.count()
            for course in tutor_courses
            if course.course_enrollment
        )

        payload = dict(upcoming_classes=schedule, active_courses=courses, total_earnings=total_earnings,
                       total_students=total_students)
        return dict(data=payload)
