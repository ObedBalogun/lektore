import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

from app.Tutee.models import TuteeProfile
from app.Tutor.models import TutorProfile
from app.chat.models import ChatThread, ChatMessage
from app.chat.serializers import MessageSerializer
from app.serializers import inline_serializer


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.thread_name = None
        self.thread = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return
        # initiate handshake
        self.accept()

        # Get or create chat thread
        self.thread_name = f"{self.scope['query_string']['thread_name']}"
        self.thread, created = ChatThread.objects.get_or_create(name=self.thread_name)

        async_to_sync(self.channel_layer.group_add)(
            self.thread_name,
            self.channel_name
        )

        self.send(text_data=json.dumps({
            'type': 'socket_connection',
            'message': 'Socket Connected'
        }))
        # fetch chat history
        messages = self.thread.messages.all().order_by("-timestamp")[:50]
        self.send(text_data=json.dumps({
            "type": "last_50_messages",
            "messages": MessageSerializer(messages, many=True).data,
        }))

    def disconnect(self, close_code):
        print("disconnected")

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json['type']

        if message_type == "chat_message":
            chat_message = ChatMessage.objects.create(
                sender=self.user,
                receiver=self.chat_receiver(),
                content=message,
                thread=self.thread
            )
            async_to_sync(self.channel_layer.group_send)(
                self.thread_name,
                {
                    "type": "chat_message_echo",
                    "name": self.user.username,
                    "message": MessageSerializer(chat_message).data,
                },
            )

    def chat_message_echo(self, event):
        self.send(json.dumps(event))

    def chat_receiver(self):
        user_ids = self.thread_name.split("__")
        for user_id in user_ids:
            user = self.get_tutor(user_id) if "LKT" in user_id else self.get_tutee(user_id)
            if user != self.user:
                return user

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