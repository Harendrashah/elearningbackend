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
    profile_image = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'role', 'email', 'profile_image', 'phone', 'otp')

    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            return request.build_absolute_uri(obj.profile_image.url)
        return None


class RegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, default='student')
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    profile_image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'phone', 'role', 'profile_image')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        role = validated_data.pop('role')
        profile_image = validated_data.pop('profile_image', None)
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=False  # User inactive until OTP verification
        )

        otp = str(random.randint(100000, 999999))

        # Update profile
        profile = user.profile
        profile.phone = phone
        profile.role = role
        profile.otp = otp
        if profile_image:
            profile.profile_image = profile_image
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
