from rest_framework import viewsets, permissions
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from common.permissions import IsInstructorOrAdmin

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

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, 'role', None)

        if role == 'student':
            return Enrollment.objects.filter(student=user)

        return Enrollment.objects.all()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
