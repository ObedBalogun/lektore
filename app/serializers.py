from rest_framework import serializers
from django.contrib.auth.models import User


def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer,), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    serializer_class = create_serializer_class(name='inline_serializer', fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


class TutorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class UserSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, required=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    username = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(max_length=15)
    gender = serializers.CharField(max_length=15)
    nationality = serializers.CharField(max_length=5)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=50)
    profile_picture = serializers.ImageField(required=False)


class UserDetailsSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, required=True)
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField(required=False)
