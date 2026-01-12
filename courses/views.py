from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, LiveClass, Enrollment
from .serializers import CourseSerializer, LiveClassSerializer, EnrollmentSerializer

# ----------------------------
# PERMISSIONS
# ----------------------------

class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Only admin or teacher can create/update/delete.
    Teacher can edit only own course/live class.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = getattr(request.user.profile, 'role', None)
        return role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        role = getattr(request.user.profile, 'role', None)
        if role == 'admin':
            return True
        if role == 'teacher':
            # Teachers can only manage their courses/classes
            return getattr(obj, 'instructor', None) == request.user or getattr(obj, 'course', None).instructor == request.user
        return False

# ----------------------------
# COURSE VIEWSET
# ----------------------------

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.filter(is_published=True)
        role = getattr(user.profile, 'role', None)
        if role in ['admin', 'teacher']:
            return Course.objects.all()
        return Course.objects.filter(is_published=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrAdmin()]
        return super().get_permissions()

# ----------------------------
# LIVE CLASS VIEWSET
# ----------------------------

class LiveClassViewSet(viewsets.ModelViewSet):
    serializer_class = LiveClassSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, 'role', None)

        if role in ['admin', 'teacher']:
            return LiveClass.objects.all()
        else:  # student
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return LiveClass.objects.filter(course_id__in=enrolled_courses)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrAdmin()]
        return [permissions.IsAuthenticated()]

# ----------------------------
# ENROLLMENT VIEWSET
# ----------------------------

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, 'role', None)
        if role == 'student':
            return Enrollment.objects.filter(student=user)
        return Enrollment.objects.all()
