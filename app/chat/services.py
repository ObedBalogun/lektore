from app.tutee.models import TuteeProfile
from app.tutor.models import TutorProfile


class ChatService:
    @classmethod
    def get_chat_receiver(cls, thread_name, sender):
        user_ids = thread_name.split("__")
        for user_id in user_ids:
            user = cls.get_tutor(user_id) if "LKT" in user_id else cls.get_tutee(user_id)
            if user != sender:
                return user

    @classmethod
    def get_user_by_id(cls, user_id):
        user, user_category_id = None, None
        try:
            user = TutorProfile.objects.get(user=user_id)
            user_category_id = user.tutor_id
        except TutorProfile.DoesNotExist:
            user = TuteeProfile.objects.get(user=user_id)
            user_category_id = user.tutee_id
        return user, user_category_id

    @classmethod
    def get_chat_history(cls, thread):
        messages = thread.messages.all().order_by("-timestamp")[:50]
        message_count = thread.messages.all().count()
        return messages, message_count

    @staticmethod
    def get_tutor(tutor_id):
        try:
            tutor = TutorProfile.objects.get(tutor_id=tutor_id)
            return tutor.user
        except TutorProfile.DoesNotExist:
            return None

    @staticmethod
    def get_tutee(tutee_id):
        try:
            tutee = TutorProfile.objects.get(tutee_id=tutee_id)
            return tutee.user
        except TuteeProfile.DoesNotExist:
            return None
