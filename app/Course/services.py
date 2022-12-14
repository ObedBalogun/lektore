from app.Course.models import Course
from app.Tutor.models import TutorProfile
from app.helpers import GenerateID
from django.forms import model_to_dict


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
            return dict(error="Error creating course")

    @classmethod
    def get_course(cls, course_id=None):
        if not course_id:
            courses = Course.objects.all()
            return dict(message="All courses retrieved successfully",
                        data=[model_to_dict(course, exclude=["id"]) for course in courses])
        try:
            course = Course.objects.get(course_id=course_id)
            return dict(data=model_to_dict(course, exclude=["id"]))
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

