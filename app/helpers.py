import string
import uuid

from django.contrib.auth import login, logout, user_logged_in, user_logged_out
from rest_framework.authtoken.models import Token
from datetime import datetime
from django.conf import settings


def user_login(request, user):
    token, _ = Token.objects.get_or_create(user=user)
    login(request, user)
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    return token


def user_logout(request):
    if Token:
        Token.objects.filter(user=request.user).delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )
    logout(request)


def generate_key(email) -> str:
    return (
            str(email).lower()
            + str(datetime.date(datetime.now()))
            + settings.SECRET_KEY
    )


class GenerateID:
    chars = string.ascii_lowercase + string.digits

    @classmethod
    def _format_id(cls, category, length):
        return f"{category}-{uuid.uuid4().hex[:length].upper()}"

    @classmethod
    def generate_id(cls, model, length) -> str:
        id_category = model.__name__.lower()
        exists = True
        generated_id = ""
        while exists:
            object_id = dict()
            if id_category == "tutorprofile":
                generated_id = cls._format_id("LKT", length)
                object_id["tutor_id"] = generated_id
            elif id_category == "tuteeprofile":
                generated_id = cls._format_id("LEK", length)
                object_id["tutee_id"] = generated_id
            elif id_category == "course":
                generated_id = cls._format_id("CRS", length)
                object_id["course_id"] = generated_id
            obj_exists = model.objects.filter(**object_id).exists()
            if not obj_exists:
                break
        return generated_id
