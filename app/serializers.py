from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializer


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
    # username = serializers.CharField(max_length=50, required=False, allow_null=True)
    phone_number = serializers.CharField(max_length=15, required=False, allow_null=True)
    gender = serializers.CharField(max_length=15)
    nationality = serializers.CharField(max_length=5)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=50)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    moving_from = serializers.CharField(required=False, allow_null=True),
    moving_to = serializers.CharField(required=False, allow_null=True)
    years_of_experience = serializers.IntegerField(min_value=0,required=False, allow_null=True)
    profession = serializers.CharField(required=False, allow_null=True)
    is_refugee = serializers.BooleanField(required=False, allow_null=True)
    services = serializers.ListSerializer(child=serializers.CharField(max_length=200,allow_null=True), required=False, allow_null=True)


class UserDetailsSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, required=True)
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField(required=False)

class CustomTokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = dict()
            refresh = self.get_token(self.context["user"])
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)
            return data
        except KeyError:
            return super().validate(attrs)

    def get_token(self, user):
        token = super().get_token(user)
        token["user_id"] = user.id
        token["last_name"] = user.last_name
        token["first_name"] = user.first_name
        token["username"] = user.email
        return token

