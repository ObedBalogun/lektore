from rest_framework import serializers


class PostOwnerSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class CommunityPostSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    post_owner = PostOwnerSerializer(read_only=True, required=False)
    post_title = serializers.CharField(max_length=50)
    post_body = serializers.CharField()
