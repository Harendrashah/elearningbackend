# notes/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Note
from .serializers import NoteSerializer
from courses.models import Enrollment

class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        role = getattr(request.user, 'profile', None) and getattr(request.user.profile, 'role', None)
        return role in ['admin', 'teacher']

class NoteViewSet(ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'profile', None) and getattr(user.profile, 'role', None)

        # URL बाट course_id र video_id तान्न
        course_id = self.request.query_params.get('course')
        video_id = self.request.query_params.get('video')

        queryset = Note.objects.all().order_by('-uploaded_at')

        # Student को लागि Enrolled Course को मात्र देखाउने
        if role == 'student':
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            queryset = queryset.filter(course_id__in=enrolled_courses)

        # Filter by course or video (if requested)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if video_id:
            queryset = queryset.filter(video_id=video_id)

        return queryset

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrTeacher()]