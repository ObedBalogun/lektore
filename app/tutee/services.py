from app.course.models import Course, Module
from app.tutee.models import TuteeProfile, TuteeProgress
from django.forms import model_to_dict


class TuteeService:
    @classmethod
    def get_tutee(cls, **kwargs) -> dict:
        if not kwargs:
            tutees = TuteeProfile.objects.select_related("user").all()
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
            tutees = TuteeProfile.objects.select_related("user").filter(
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
        registered_course = TuteeProfile.objects.select_related("tutee").get(
            module__id=kwargs.get("module_id"),
            tutee__tutee_id=kwargs.get("tutee_id"))

        for key, value in kwargs.items():
            if key not in ["tutee_id", "module_id"] and not getattr(registered_course, key):
                setattr(registered_course, key, value)
        registered_course.save()

        return dict(data=model_to_dict(registered_course), message="Course has been updated")

    @classmethod
    def get_tutee_courses(cls, request):
        if not request.GET.keys():
            tutee = TuteeProfile.objects.prefetch_related("courses").get(user__email=request.user)
            registered_courses = tutee.courses.all()
            data = [dict(course_name=course.course_name, course_id=course.course_id) for course in registered_courses]
            return dict(data=data, message="Tutee Courses Retrieved")

        else:
            course_id = request.GET.get("course_id")
            tutee_course_progress = TuteeProgress.objects.select_related("module","course").filter(course__course_id=course_id,
                                                                 tutee__user__email=request.user)
            course = tutee_course_progress.first().course
            return dict(data=dict(
                course_name=course.course_name,
                modules=[
                    dict(
                        module_name=module.module.module_name,
                        module_video=module.module.module_video,
                        module_audio=module.module.module_audio,
                        module_pdf=module.module.module_pdf,
                        is_module_video_completed=module.is_module_video_completed,
                        is_module_audio_completed=module.is_module_audio_completed,
                        is_module_pdf_completed=module.is_module_pdf_completed,
                    ) for module in tutee_course_progress]), message="Course Successfully retrieved")

    @classmethod
    def register_course(cls, **kwargs):
        course = Course.objects.get(course_id=kwargs.get("course_id"))
        module = Module.objects.get(course_id=kwargs.get("course_id"))
