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
