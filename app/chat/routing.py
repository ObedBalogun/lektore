from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/socket-server/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/chat-thread/$', consumers.ChatConsumer.as_asgi())

]