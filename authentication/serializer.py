from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']  
#se crea un serializer para hacer que los datos dados se convierten en json

class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['password']