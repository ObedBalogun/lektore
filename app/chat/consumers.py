import json
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
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
        # get request user and attempt to authenticate
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return
        # initiate handshake
        self.accept()

        # Get or create chat thread
        self.thread_name = f"{self.scope['query_string']['thread_name']}"
        self.thread, created = ChatThread.objects.get_or_create(name=self.thread_name)
        # add this channel to broadcast group
        async_to_sync(self.channel_layer.group_add)(
            self.thread_name,
            self.channel_name
        )
        # display socket connection status
        self.send(text_data=json.dumps(
            {
                'type': 'socket_connection',
                'message': 'Socket Connected'
            }
        ))
        # Get and display online users
        self.thread.online_users.add(self.user)
        self.send(text_data=json.dumps(
            {
                "type": "online_user_list",
                "users": [user.username for user in self.thread.online_users.all()],
            }
        ))
        # fetch and display chat history
        messages, message_count = ChatService.get_chat_history(self.thread)
        self.send(text_data=json.dumps(
            {
                "type": "last_50_messages",
                "messages": ChatMessageSerializer(messages, many=True).data,
                "has_more": message_count > 50,
            }
        ))

    def disconnect(self, close_code):
        print("disconnected")
        self.thread.online_users.remove(self.user)
        async_to_sync(self.channel_layer.group_discard)(self.thread_name, self.channel_name)
        return super().disconnect(close_code)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == "chat_message":
            message = text_data_json['message']
            chat_message = ChatMessage.objects.create(
                sender=self.user,
                receiver=ChatService.get_chat_receiver(self.thread_name, self.user),
                content=message,
                thread=self.thread
            )
            async_to_sync(self.channel_layer.group_send)(
                self.thread_name,
                {
                    "type": "broadcast_message",
                    "name": self.user.username,
                    "message": ChatMessageSerializer(chat_message).data,
                },
            )
        elif message_type == "typing":
            async_to_sync(self.channel_layer.group_send)(
                self.thread_name,
                {
                    "type": "typing",
                    "user": self.user.first_name,
                    "typing": text_data_json["typing"],
                },
            )

    ##########Event Methods##########
    def broadcast_message(self, event):
        self.send(json.dumps(event))

    def typing(self, event):
        self.send(json.dumps(event))


class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()
        unread_messages_count = ChatMessage.objects.filter(receiver=self.user, read=False).count()
        self.send_json(
            {
                "type": "unread_count",
                "unread_count": unread_messages_count,
            }
)

