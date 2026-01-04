# serializers.py
import random
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


# Profile Serializer for read
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'role', 'email', 'profile_image', 'phone', 'otp')


# Profile Update Serializer for edit
class ProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'phone', 'profile_image']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            instance.user.last_name = user_data['last_name']
        instance.user.save()
        return super().update(instance, validated_data)


# Registration Serializer
class RegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, default='student')
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'role')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        role = validated_data.pop('role')
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=False  # OTP verify
        )

        otp = str(random.randint(100000, 999999))

        profile = user.profile
        profile.phone = phone
        profile.role = role
        profile.otp = otp
        profile.save()

        return user
