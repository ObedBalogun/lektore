from app.schedule.models import Schedule, Availability
from django.forms import model_to_dict
import datetime
from django.contrib.auth import get_user_model


class ScheduleService:
    @classmethod
    def create_schedule(cls, **kwargs):
        user = get_user_model().objects.get(id=kwargs.get("user"))
        title = kwargs.get("title")
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        description = kwargs.get("description")
        schedule_type = kwargs.get("schedule_type")
        actual_start_date, string_start_date = cls.format_date(start_time)
        actual_end_date, string_end_date = cls.format_date(end_time)
        try:
            if schedule := Schedule.objects.get(**kwargs):
                return dict(error="Schedule already exists")
        except Schedule.DoesNotExist:
            try:
                user_availability = Availability.objects.get(user=user)
                user_availability = cls.check_availability(user_availability, actual_start_date, actual_end_date)
                if user_availability:
                    schedule = Schedule.objects.create(
                        user=user,
                        title=title,
                        start_time=actual_start_date,
                        end_time=actual_end_date,
                        description=description,
                        schedule_type=schedule_type
                    )
                    return dict(
                        message=f"Schedule for {string_start_date.split(',')[0]} at {string_start_date.split(',')[1]} "
                                "created successfully")
                else:
                    return dict(error="Selected time is not available")
            except Availability.DoesNotExist:
                return dict(error="User availability not set")

    @classmethod
    def get_schedule_by_user(cls, request, schedule_id=None):
        if not schedule_id:
            user = request.user
            if schedules := Schedule.objects.filter(user=user):
                return dict(data=[model_to_dict(schedule, exclude=["id"]) for schedule in schedules])
            return dict(message="No schedules found")
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            return dict(data=model_to_dict(schedule, exclude=["id"]))
        except Schedule.DoesNotExist:
            return dict(message="Schedule does not exist")

    @classmethod
    def update_schedule(cls, **kwargs):
        schedule_id = kwargs.get("schedule_id")
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            for key, value in kwargs.items():
                if key != "schedule_id":
                    setattr(schedule, key, value)
            schedule.save()
            return dict(message="Schedule updated successfully")
        except Schedule.DoesNotExist:
            return dict(error="Schedule does not exist")

    @classmethod
    def delete_schedule(cls, pk):
        try:
            schedule = Schedule.objects.get(id=pk)
            schedule.delete()
            return dict(message="Schedule deleted successfully")
        except Schedule.DoesNotExist:
            return dict(error="Schedule does not exist")

    @classmethod
    def create_availability(cls, **kwargs):
        user = get_user_model().objects.get(id=kwargs.get("user"))
        times_dict = {
            key: cls.format_times(value)
            for key, value in kwargs.items()
            if key != "user"
        }
        try:
            if availability := Availability.objects.get(user=user):
                return dict(error="Availability already exists")
        except Availability.DoesNotExist:
            data = dict(user=user, **times_dict)
            availability = Availability.objects.create(**data)
            return dict(message="Availability created successfully")

    @classmethod
    def get_availability(cls, request):
        user = get_user_model().objects.get(id=request.user.id)
        try:
            if availability := Availability.objects.get(user=user):
                return dict(data=model_to_dict(availability, exclude=["id"]))
        except Availability.DoesNotExist:
            return dict(error="User availability not set")

    @classmethod
    def update_availability(cls, **kwargs):
        user = get_user_model().objects.get(id=kwargs.get("user"))
        try:
            availability = Availability.objects.get(user=user)
            for key, value in kwargs.items():
                if key != "user":
                    setattr(availability, key, value)
            availability.save()
            return dict(message="Availability updated successfully")
        except Availability.DoesNotExist:
            return dict(error="Availability does not exist")

    @staticmethod
    def format_date(date):
        actual_format = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%fZ")
        string_format = actual_format.strftime("%d %B %Y,%H:%m")
        return actual_format, string_format

    @staticmethod
    def format_times(timeslots):
        time_list = ()
        for timeslot in timeslots:
            time_list += timeslot,
        return time_list

    @staticmethod
    def day_of_week(date):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[date.weekday()].lower()

    @classmethod
    def check_availability(cls, user_availability, string_start_date, string_end_date):
        day_of_week = cls.day_of_week(string_start_date)
        schedule_start_time = str(string_start_date).split(" ")[1][:5]  # 12:00
        schedule_end_time = str(string_end_date).split(" ")[1][:5]  # 13:00
        '''
        Schedules cant be created on days that are not available.
        Schedules cant be created on days that are available but 
        not within the available times.
        '''
        if day_of_week in user_availability.__dict__:
            available_times = getattr(user_availability, day_of_week)
            for period in available_times:
                availability_start_time, availability_end_time = period.split("-")
                if int(availability_start_time.replace(":", "")) <= int(schedule_start_time.replace(":", "")) <= int(
                        availability_end_time.replace(":", "")):
                    print(availability_start_time, availability_end_time, schedule_start_time, schedule_end_time)
                    return int(schedule_end_time.replace(":", "")) <= int(
                        availability_end_time.replace(":", "")
                    )
            return False
        return False
