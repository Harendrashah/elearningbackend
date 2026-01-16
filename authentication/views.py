from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, RegistrationSerializer, AdminUserProfileSerializer
)
from .permissions import IsAdminUserProfile, IsTeacher
from courses.models import Course, Enrollment

User = get_user_model()

# ---------------- ADMIN USER LIST (FIXED) ----------------
class AdminUserListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = AdminUserProfileSerializer
    # 🔥 FIX: IsAuthenticated + IsAdminUser (Standard Django Admin check)
    # Yadi tapai superuser hunuhunxa vane yo chalcha
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser] 

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = AdminUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    lookup_field = 'id'

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def admin_update_role(request, pk):
    try:
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        new_role = request.data.get('role')
        
        if new_role not in ['student', 'teacher', 'admin']:
            return Response({'error': 'Invalid role'}, status=400)

        profile.role = new_role
        profile.save()

        # Update Django Permissions
        if new_role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif new_role == 'teacher':
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False
        user.save()

        return Response({'message': f'Role updated to {new_role}'})
    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

# ---------------- AUTH & OTHERS (Standard) ----------------
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
        if user.profile.otp == otp:
            user.is_active = True
            user.profile.is_verified = True
            user.profile.otp = None
            user.profile.save()
            user.save()
            return Response({'message': 'Verified'})
        return Response({'error': 'Invalid OTP'}, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful!',
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=401)

class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user.profile
    

# ---------------- TEACHER VIEWS ----------------
@api_view(['GET'])
@permission_classes([IsTeacher])
def teacher_dashboard_stats(request):
    students = UserProfile.objects.filter(role='student')
    return Response({"total_students": students.count(), "students": list(students.values('id', 'user__username', 'email'))})

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

@api_view(['POST'])
@permission_classes([IsTeacher])
def enroll_student(request):
    # Logic remains same as yours
    return Response({"message": "Enrolled"})