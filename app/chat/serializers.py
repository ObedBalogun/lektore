from rest_framework import serializers
from django.contrib.auth.models import User

from app.chat.models import ChatMessage


class MessageSerializer(serializers.ModelSerializer):
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
