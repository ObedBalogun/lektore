from app.chat.models import ChatThread, ChatMessage
from app.chat.serializers import ChatThreadSerializer, ChatMessageSerializer
from rest_framework.generics import get_object_or_404
from rest_framework import permissions
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from app.chat.services import ChatService


class ChatThreadViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChatThreadSerializer
    queryset = ChatThread.objects.none()
    lookup_field = "name"

    def get_queryset(self):
        user, user_id = ChatService.get_user_by_id(self.request.user.id)
        return ChatThread.objects.filter(name__contains=str(user_id))

    def get_serializer_context(self):
        return {"request": self.request, "user": self.request.user}


class ChatMessageViewSet(ListModelMixin, GenericViewSet):
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.none()
    paginate_by = 50

    def get_queryset(self):
        thread_name = self.request.GET.get("thread_name")
        user, user_id = ChatService.get_user_by_id(self.request.user.id)
        return (
            ChatMessage.objects.filter(
                thread__name__contains=str(user_id),
            )
            .filter(thread__name=thread_name)
            .order_by("-timestamp")
        )
