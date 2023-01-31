from app.tutor.models import TutorProfile
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
