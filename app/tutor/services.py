from app.tutor.models import TutorProfile, EducationalQualification
from django.forms import model_to_dict

from app.tutor.serializers import TutorSerializer


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
                return dict(error="Education already exists for user")
        except EducationalQualification.DoesNotExist:
            education = EducationalQualification.objects.create(
                tutor=tutor_profile,
                **kwargs
            )
            return dict(message="Education created successfully",
                        data=model_to_dict(education, exclude=["id"]))
