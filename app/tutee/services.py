from app.tutee.models import TuteeProfile
from django.forms import model_to_dict


class TuteeService:
    @classmethod
    def get_tutee(cls, **kwargs) -> dict:
        if not kwargs:
            tutees = TuteeProfile.objects.all()
            return dict(message="All tutees retrieved successfully",
                        data=[dict(
                            tutee=dict(
                                first_name=tutee.user.first_name,
                                last_name=tutee.user.last_name,
                                tutee_id=tutee.tutee_id,
                                date_of_birth=tutee.date_of_birth.strftime("%d %B %Y")),
                            phone_number=tutee.phone_number,
                            postal_code=tutee.postal_code,
                            address=tutee.address,
                            state=tutee.current_state,
                            country=tutee.current_country.name,
                            nationality=tutee.nationality.name,
                            is_qualified=tutee.is_qualified
                        ) for tutee in tutees])
        try:
            tutees = TuteeProfile.objects.select_related("user").prefetch_related("tutee_course_class__course").filter(
                **kwargs)
            return dict(message="Tutees retrieved successfully",
                        data=[dict(
                            tutee=dict(
                                first_name=tutee.user.first_name,
                                last_name=tutee.user.last_name,
                                tutee_id=tutee.tutee_id,
                                date_of_birth=tutee.date_of_birth.strftime("%d %B %Y")),
                            phone_number=tutee.phone_number,
                            postal_code=tutee.postal_code,
                            address=tutee.address,
                            state=tutee.current_state,
                            country=tutee.current_country.name,
                            nationality=tutee.nationality.name,
                            is_qualified=tutee.is_qualified
                        ) for tutee in tutees])
        except Exception as e:
            print(str(e))
            return dict(error="Tutee does not exist")
