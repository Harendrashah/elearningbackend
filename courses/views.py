from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Enrollment, Content
from .serializers import CourseSerializer, EnrollmentSerializer, ContentSerializer


# =========================================================
# PERMISSIONS
# =========================================================

class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Only admin or teacher can create/update/delete.
    Teacher can edit only own course/content.
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
            return getattr(obj, 'instructor', None) == request.user

        return False


class IsEnrolled(permissions.BasePermission):
    """
    Student must be enrolled to view course contents
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        course_id = view.kwargs.get('course_pk')
        if not course_id:
            return False

        return Enrollment.objects.filter(
            student=request.user,
            course_id=course_id
        ).exists()


# =========================================================
# COURSE VIEWSET
# =========================================================

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        # Public users
        if not user.is_authenticated:
            return Course.objects.filter(is_published=True)

        role = getattr(user.profile, 'role', None)

        # Admin & teacher can see all
        if role in ['admin', 'teacher']:
            return Course.objects.all()

        # Student can see only published
        return Course.objects.filter(is_published=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        role = getattr(request.user.profile, 'role', None)

        # ❌ Teacher & Admin cannot enroll
        if role != 'student':
            return Response(
                {'detail': 'Only students can enroll in courses.'},
                status=status.HTTP_403_FORBIDDEN
            )

        course = self.get_object()

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )

        if created:
            return Response(
                {'message': 'Successfully enrolled.'},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'message': 'Already enrolled.'},
            status=status.HTTP_200_OK
        )


# =========================================================
# CONTENT VIEWSET (VIDEOS, DOCS, BOOKS)
# =========================================================

class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer

    def get_queryset(self):
        course_id = self.kwargs.get('course_pk')
        return Content.objects.filter(course_id=course_id)

    def get_permissions(self):
        # ❌ Student cannot create/update/delete content
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrAdmin()]

        # ✅ Only enrolled students can view content
        return [permissions.IsAuthenticated(), IsEnrolled()]
