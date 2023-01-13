import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from app.chat.models import ChatThread, ChatMessage
from app.chat.serializers import ChatMessageSerializer
from app.chat.services import ChatService


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
        # messages = self.thread.messages.all().order_by("-timestamp")[:50]
        # self.send(text_data=json.dumps({
        #     "type": "last_50_messages",
        #     "messages": ChatMessageSerializer(messages, many=True).data,
        # }))
        messages = self.thread.messages.all().order_by("-timestamp")[:50]
        message_count = self.thread.messages.all().count()
        self.send(text_data=json.dumps(
            {
                "type": "last_50_messages",
                "messages": ChatMessageSerializer(messages, many=True).data,
                "has_more": message_count > 50,
            }
        ))

    def disconnect(self, close_code):
        print("disconnected")

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json['type']

        if message_type == "chat_message":
            chat_message = ChatMessage.objects.create(
                sender=self.user,
                receiver=ChatService.get_chat_receiver(self.thread_name, self.user),
                content=message,
                thread=self.thread
            )
            async_to_sync(self.channel_layer.group_send)(
                self.thread_name,
                {
                    "type": "chat_message_echo",
                    "name": self.user.username,
                    "message": ChatMessageSerializer(chat_message).data,
                },
            )

    def chat_message_echo(self, event):
        self.send(json.dumps(event))

