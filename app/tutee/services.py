from app.course.models import Course
from app.tutee.models import TuteeProfile, RegisteredTuteeCourse
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

    @classmethod
    def purchase_course(cls, **kwargs):
        cart_items = kwargs.get("cart_items")
        for cart_item in cart_items:
            course_id = cart_item.get("course_id")
            # TODO: register course and create object
            course = Course.objects.get(course_id=course_id)

    @classmethod
    def update_course(cls, **kwargs):
        registered_course = RegisteredTuteeCourse.objects.select_related("tutee").get(
            module__id=kwargs.get("module_id"),
            tutee__tutee_id=kwargs.get("tutee_id"))

        for key, value in kwargs.items():
            if key not in ["tutee_id", "module_id"] and not getattr(registered_course, key):
                setattr(registered_course, key, value)
        registered_course.save()

        return dict(data=model_to_dict(registered_course), message="Course has been updated")
