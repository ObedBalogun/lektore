import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = "lol"
        self.user = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return
        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name,
        )

        self.send(text_data=json.dumps({
            'type': 'socket_connection',
            'message': 'Socket Connected'
        }))

    def disconnect(self, close_code):
        print("disconnected")

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                "type": "chat_message_echo",
                "name": text_data_json["name"],
                "message": text_data_json["message"],
            },
        )

    def chat_message_echo(self, event):
        print(event)
        self.send(json.dumps(event))

