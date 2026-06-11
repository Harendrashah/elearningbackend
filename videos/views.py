from rest_framework import viewsets, parsers, permissions
from .models import Video
from .serializers import VideoSerializer
from courses.models import Enrollment

class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    # ✅ JSONParser add gareko — PATCH request ko lagi
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,      # ✅ ADD GAREKO
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course')

        if user.is_staff:
            if course_id:
                return Video.objects.filter(course_id=course_id).order_by('created_at')
            return Video.objects.all().order_by('-created_at')

        if course_id:
            is_enrolled = Enrollment.objects.filter(
                student=user, course_id=course_id
            ).exists()
            if is_enrolled:
                return Video.objects.filter(course_id=course_id).order_by('created_at')

        return Video.objects.none()