from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import LiveSession
from .serializers import LiveSessionSerializer
from common.permissions import IsInstructorOrAdmin
from courses.models import Enrollment

class LiveSessionViewSet(ModelViewSet):
    serializer_class = LiveSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, 'role', None)

        if role in ['admin', 'teacher']:
            return LiveSession.objects.all()

        enrolled_courses = Enrollment.objects.filter(
            student=user
        ).values_list('course', flat=True)

        return LiveSession.objects.filter(course_id__in=enrolled_courses)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsInstructorOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
