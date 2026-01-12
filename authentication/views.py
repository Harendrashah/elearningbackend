from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, RegistrationSerializer, AdminUserProfileSerializer
)
from .permissions import IsAdminUserProfile, IsTeacher
from courses.models import Course, Enrollment
import random

# ---------------- Teacher Dashboard Stats & Students ----------------
@api_view(['GET'])
@permission_classes([IsTeacher])
def teacher_dashboard_stats(request):
    students = UserProfile.objects.filter(role='student')
    student_count = students.count()
    student_list = students.values('id', 'user__username', 'email')
    return Response({
        "total_students": student_count,
        "students": list(student_list)
    })

# ---------------- Teacher Student List/Detail ----------------
class TeacherStudentListView(generics.ListAPIView):
    serializer_class = AdminUserProfileSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return UserProfile.objects.filter(role='student')

class TeacherStudentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserProfileSerializer
    permission_classes = [IsTeacher]
    lookup_field = 'id'

    def get_queryset(self):
        return UserProfile.objects.filter(role='student')

# ---------------- Teacher Enroll Student ----------------
@api_view(['POST'])
@permission_classes([IsTeacher])
def enroll_student(request):
    student_id = request.data.get('student_id')
    course_id = request.data.get('course_id')

    student_profile = UserProfile.objects.get(id=student_id, role='student')
    course = Course.objects.get(id=course_id, teacher=request.user)

    Enrollment.objects.create(student=student_profile.user, course=course)
    return Response({"message": "Student enrolled successfully"})

# ---------------- User Profile ----------------
class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user.profile

# ---------------- Registration & OTP ----------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully!',
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            profile.save()
            user.save()
            return Response({'message': 'Account verified successfully'})
        return Response({'error': 'Invalid OTP'}, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

# ---------------- Login ----------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        if not user.is_active:
            return Response({'error': 'Account not verified.'}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful!',
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=401)

# ---------------- Admin User List/Detail ----------------
class AdminUserListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = AdminUserProfileSerializer
    permission_classes = [IsAdminUserProfile]

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = AdminUserProfileSerializer
    permission_classes = [IsAdminUserProfile]
    lookup_field = 'id'
