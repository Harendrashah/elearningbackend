# instructors/serializers.py
from rest_framework import serializers
from .models import Instructor
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'

    # Yo function le garda Frontend ma User ko ID ko satta purai details जान्छ
    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.user:
            response['user'] = UserSerializer(instance.user).data
        return response