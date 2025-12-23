from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Enrollment, Content  # <-- ensure Course, Enrollment, Content imported
from .serializers import CourseSerializer, EnrollmentSerializer, ContentSerializer

# ---------------- PERMISSIONS ----------------

class IsInstructorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            getattr(obj, 'instructor', None) == request.user
            or getattr(request.user.profile, 'role', None) == 'admin'
        )

class IsEnrolled(permissions.BasePermission):
    def has_permission(self, request, view):
        course_id = view.kwargs.get('course_pk') or view.kwargs.get('pk')
        return Enrollment.objects.filter(
            student=request.user,
            course_id=course_id
        ).exists()

# ---------------- COURSE ----------------

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsInstructorOrAdmin]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        if created:
            return Response({'message': 'Successfully enrolled.'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already enrolled.'}, status=status.HTTP_200_OK)

# ---------------- CONTENT (VIDEOS, MATERIALS, BOOKS ETC) ----------------

class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer

    def get_queryset(self):
        course_id = self.kwargs.get('course_pk')
        return Content.objects.filter(course_id=course_id)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructorOrAdmin()]
        return [permissions.IsAuthenticated(), IsEnrolled()]
