from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Note
from .serializers import NoteSerializer
from courses.models import Enrollment

class NoteViewSet(ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, 'role', None)

        if role == 'student':
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return Note.objects.filter(course_id__in=enrolled_courses)
        return Note.objects.all()
