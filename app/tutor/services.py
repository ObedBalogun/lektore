from datetime import datetime

from django.db.models import Sum

from app.course.models import Course
# from app.schedule.models import Schedule
from app.tutor.models import TutorProfile, EducationalQualification
from django.forms import model_to_dict

from app.tutor.serializers import TutorSerializer
from app.wallet.models import Wallet


class TutorService:
    @classmethod
    def tutor_dashboard(cls, request):
        tutor = TutorProfile.objects.prefetch_related("purchased_courses").get(
            user=request.user)
        courses = tutor.courses.count()
        user_wallet = Wallet.objects.get(user=request.user)
        total_withdrawals = user_wallet.wallet_transactions.filter(transaction_type="debit",
                                                                   payment_status=True).aggregate(Sum("amount"))
        tutor_courses = tutor.courses.all()
        purchased_courses = len(set(tutor.purchased_courses.all()))
        overall_purchases = tutor.purchased_courses.filter(purchase_status=True).count()

        # total_students = sum(
        #     course.tutee_orders.count()
        #     for course in tutor_courses
        #     if hasattr(course, "tutor_courses")
        # )

        payload = dict(courses=courses, total_purchased_courses=overall_purchases,
                       purchased_courses=purchased_courses, total_withdrawals=total_withdrawals.get("amount__sum") or 0,
                       cover_image=tutor.dashboard_wallpaper)
                       # tutor_courses=[(course.course_id,course.course_name) for course in tutor_courses])
        return dict(data=payload, message="Tutor Dashboard")

    @classmethod
    def get_tutor(cls, **kwargs) -> dict:
        tutor_id = kwargs.get("tutor_id")
        if not tutor_id:
            tutors = TutorProfile.objects.all()
            serialized_data = TutorSerializer(data=tutors, many=True)
            serialized_data.is_valid(raise_exception=False)

            return dict(message="All tutors retrieved successfully",
                        data=serialized_data.data)
        try:
            tutor = TutorProfile.objects.get(tutor_id=tutor_id)
            serialized_data = TutorSerializer(tutor)
            return dict(data=serialized_data.data, message="Tutor retrieved successfully")
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
