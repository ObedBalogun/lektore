from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from django.db import close_old_connections


class TokenAuthMiddleware:
    """
    Custom middleware that takes a token from the headers
     and authenticates via Django Rest Framework authtoken.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            try:
                token_key = headers[b'authorization'].decode().split()[0]
                scope["token"] = token_key
                scope["user"] = await self.get_user(scope)
            except (KeyError, Token.DoesNotExist):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, scope):
        """
        Return the user model instance associated with the given scope.
        If no user is retrieved, return an instance of `AnonymousUser`.
        """
        if "token" not in scope:
            raise ValueError(
                "Cannot find token in scope. You should wrap your consumer in "
                "TokenAuthMiddleware."
            )
        token = scope["token"]
        user = None
        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            raise AuthenticationFailed(_("Invalid token."))
        if user is None:
            user = AnonymousUser()
        close_old_connections()
        return user
