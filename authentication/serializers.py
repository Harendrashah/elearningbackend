# serializers.py
import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'role', 'bio', 'profile_image', 'phone', 'otp')  # otp optional

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
            is_active=False  # 🔥 OTP verify pachi matra active
        )

        otp = str(random.randint(100000, 999999))

        profile = user.profile
        profile.phone = phone
        profile.role = role
        profile.otp = otp  # OTP field must exist in UserProfile
        profile.save()

        # Send OTP email
        send_mail(
            subject='Your OTP Verification Code',
            message=f'Your OTP is {otp}',
            from_email='sahh8645@gmail.com',
            recipient_list=[user.email],
            fail_silently=False
        )

        return user
