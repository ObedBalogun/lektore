from app.course.models import Course, Module
from app.tutor.models import TutorProfile
from app.helpers import GenerateID
from django.forms import model_to_dict
from django.db.models import Q


class CourseService:
    @classmethod
    def create_course(cls, **kwargs):
        course_details = kwargs.copy()
        course_code = GenerateID.generate_id(Course, 3)
        course_details['course_id'] = course_code
        tutor_id = kwargs.get("tutor_id")
        try:
            tutor = TutorProfile.objects.get(tutor_id=tutor_id)
            course_details['tutor_id'] = tutor.id
            course = Course.objects.create(**course_details)
            return dict(message=f"{tutor.user.first_name}'s course, {course.course_name}, created successfully",
                        data=model_to_dict(course, exclude=["id"]))
        except TutorProfile.DoesNotExist:
            return dict(error=f"Tutor with id {tutor_id} does not exist for this course")
        except Exception as e:
            return dict(error=f"Error {e}")

    @classmethod
    def get_course(cls, **kwargs):
        if not kwargs:
            courses = Course.objects.select_related("tutor", "tutor__user").prefetch_related("registered_tutees").all()
            return dict(message="All courses retrieved successfully",
                        data=[dict(course_name=course.course_name,
                                   course_id=course.course_id,
                                   course_overview=course.course_overview,
                                   course_price=course.course_price,
                                   tutor=dict(tutor_id=course.tutor.tutor_id,
                                              tutor_name=course.tutor.user.get_full_name()),
                                   created_date=course.created.strftime("%d %B %Y"),
                                   download_count=course.registered_tutees.count(),
                                   ) for course in courses])
        try:
            courses = Course.objects.select_related("tutor", "tutor__user").prefetch_related(
                "registered_tutees").filter(**kwargs)
            return dict(data=[dict(course_name=course.course_name,
                                   course_id=course.course_id,
                                   course_overview=course.course_overview,
                                   course_price=course.course_price,
                                   tutor=dict(tutor_id=course.tutor.tutor_id,
                                              tutor_name=course.tutor.user.get_full_name()),
                                   created_date=course.created.strftime("%d %B %Y"),
                                   download_count=course.registered_tutees.count(),
                                   )
                              for course in courses],
                        message="All courses retrieved successfully")
        except Course.DoesNotExist:
            return dict(error="Course does not exist")

    @classmethod
    def get_course_by_tutor(cls, tutor_id):
        try:
            tutor = TutorProfile.objects.get(tutor_id=tutor_id)
            courses = Course.objects.filter(tutor_id=tutor.id)
            return dict(message=f"{tutor.user.first_name}'s courses retrieved successfully",
                        data=[model_to_dict(course, exclude=["id"]) for course in courses])
        except TutorProfile.DoesNotExist:
            return dict(error="Tutor does not exist")

    @classmethod
    def delete_course(cls, course_id):
        try:
            course = Course.objects.get(course_id=course_id)
            course.delete()
            return dict(message=f"{course.course_name} deleted successfully")
        except Course.DoesNotExist:
            return dict(error=f"Course {course_id} does not exist")


class ModuleService:
    @classmethod
    def create_module(cls, **kwargs):
        module_details = kwargs.copy()
        course_id = kwargs.get("course_id")
        try:
            course = Course.objects.get(course_id=course_id)
            print(course, course_id)
            module_details['course'] = course
            module_details.pop("course_id")
            module = Module.objects.create(**module_details)
            return dict(message=f"module for course, {course.course_name}, created successfully",
                        data=model_to_dict(module, exclude=["id"]))
        except Course.DoesNotExist:
            return dict(error="Error creating module")

    @classmethod
    def get_modules(cls, **kwargs):
        if not kwargs:
            modules = Module.objects.select_related("course").all()
            return dict(message="All modules retrieved successfully",
                        data=[dict(
                            module_id=module.id,
                            course_name=module.course.course_name,
                            course_id=module.course.course_id,
                            created_date=module.course.created.strftime("%d %B %Y"),
                            module_description=module.module_description,
                            module_duration=module.module_duration,
                            module_video=module.module_video,
                            module_audio=module.module_audio,
                            module_pdf=module.module_pdf,
                        ) for module in modules])
        try:
            filterset = kwargs.copy()
            if "course_id" in filterset:
                filterset["course__course_id"] = filterset.pop("course_id")
            filterset = {f"{key}__icontains": value for key, value in filterset.items()}
            modules = Module.objects.select_related("course").filter(**filterset).order_by("created")
            return dict(data=[dict(module_id=module.id,
                                   course_name=module.course.course_name,
                                   course_id=module.course.course_id,
                                   created_date=module.course.created.strftime("%d %B %Y"),
                                   module_description=module.module_description,
                                   module_duration=module.module_duration,
                                   module_video=module.module_video,
                                   module_audio=module.module_audio,
                                   module_pdf=module.module_pdf,
                                   ) for module in modules],
                        message="Modules retrieved successfully")
        except Course.DoesNotExist:
            return dict(error="Course does not exist")

    @classmethod
    def update_module(cls, **kwargs):
        module = Module.objects.get(id=kwargs.get("module_id"))
        for key, value in kwargs.items():
            if key not in ["tutee_id", "course_id"]:
                setattr(module, key, value)
