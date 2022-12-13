from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, required=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(max_length=15)
    gender = serializers.CharField(max_length=15)
    nationality = serializers.CharField(max_length=5)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=50)



class UserDetailsSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, required=True)
    username = serializers.EmailField()
