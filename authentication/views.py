# views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer, RegistrationSerializer
from .permissions import IsAdminUserProfile
import random
from django.core.mail import send_mail
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    RegistrationSerializer,
    AdminUserProfileSerializer
)


# -------------------------
# User Profile View
# -------------------------
class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

# -------------------------
# Registration View
# -------------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Send OTP email (already handled in serializer if you merged OTP logic)
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully! Please verify OTP sent to your email.',
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------
# OTP Verification View
# -------------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    username = request.data.get('username')
    otp = request.data.get('otp')

    try:
        user = User.objects.get(username=username)
        profile = user.profile

        if profile.otp == otp:
            user.is_active = True
            profile.is_verified = True
            profile.otp = None
            profile.email = user.email  # Update email in profile
            user.save()
            profile.save()

            return Response({'message': 'Account verified successfully'})

        return Response({'error': 'Invalid OTP'}, status=400)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

# -------------------------
# Login View
# -------------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        if not user.is_active:
            return Response({'error': 'Account not verified. Please check your email for OTP.'}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful!',
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# -------------------------
# Admin Views
# -------------------------
class AdminUserListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUserProfile]

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUserProfile]
    lookup_field = 'id'

class AdminUserListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = AdminUserProfileSerializer
    permission_classes = [IsAdminUserProfile]


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = AdminUserProfileSerializer
    permission_classes = [IsAdminUserProfile]
    lookup_field = 'id'
