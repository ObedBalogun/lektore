from rest_framework import serializers
from django.contrib.auth.models import User

from app.chat.models import ChatMessage, ChatThread
from app.chat.services import ChatService


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    # receiver = serializers.SerializerMethodField()
    # thread = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ["sender", "content", "read"]

    # def get_thread(self, obj):
    #     return str(obj.thread.id)

    def get_sender(self, obj):
        return UserSerializer(obj.sender).data

    # def get_receiver(self, obj):
    #     return UserSerializer(obj.receiver).data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class ChatThreadSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatThread
        fields = ("id", "name", "other_user", "last_message")

    def get_last_message(self, obj):
        messages = obj.messages.all().order_by("-timestamp")
        if not messages.exists():
            return None
        message = messages[0]
        return ChatMessageSerializer(message).data

    def get_other_user(self, obj):
        context = {}
        user = ChatService.get_chat_receiver(obj.name, self.context["request"].user)
        return UserSerializer(user, context=context).data