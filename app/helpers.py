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
