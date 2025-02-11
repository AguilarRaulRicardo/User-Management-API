from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "email"]


# se crea un serializer para hacer que los datos dados se convierten en json


class ChangePasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=70)
    password = serializers.CharField(max_length=150)
    new_password = serializers.CharField(max_length=150)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=70)
    password = serializers.CharField(max_length=150)
