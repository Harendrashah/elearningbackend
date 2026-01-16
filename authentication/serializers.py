import random
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile

# --- ADMIN / TEACHER USER LIST SERIALIZER ---
class AdminUserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    password = serializers.CharField(write_only=True, required=False)
    
    # 🔥 FIX: Frontend lai User ID chaincha, Profile ID haina
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = UserProfile
        # 'user_id' add gareko chu list ma:
        fields = ['id', 'user_id', 'username', 'email', 'password', 'role', 'phone', 'profile_image']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        password = validated_data.pop('password', None)
        user = instance.user

        if 'username' in user_data:
            user.username = user_data['username']
        if 'email' in user_data:
            user.email = user_data['email']
        if password:
            user.set_password(password)

        user.save()
        return super().update(instance, validated_data)

# --- USER SERIALIZER ---
class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')

# --- PROFILE SERIALIZER ---
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ('user', 'role', 'email', 'profile_image', 'phone', 'otp')

# --- REGISTRATION SERIALIZER ---
class RegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=True
        )
        otp = str(random.randint(100000, 999999))
        profile = user.profile
        profile.phone = phone
        profile.role = 'student'
        profile.otp = otp
        profile.save()
        return user