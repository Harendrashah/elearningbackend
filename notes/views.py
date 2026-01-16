# notes/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Note
from .serializers import NoteSerializer
from courses.models import Enrollment

# --- ✅ 1. YO CLASS THAPNU HOS ---
class IsAdminOrTeacher(BasePermission):
    """
    Custom Permission:
    - Admin ra Teacher le matra create/delete garna pauchan.
    """
    def has_permission(self, request, view):
        # User login huna paryo
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser lai sadhai allow garne
        if request.user.is_superuser:
            return True

        # Profile check garne
        role = getattr(request.user, 'profile', None) and getattr(request.user.profile, 'role', None)
        return role in ['admin', 'teacher']
# -----------------------------------


class NoteViewSet(ModelViewSet):
    serializer_class = NoteSerializer
    # Default permission (sabai le herna milcha yadi login cha bhane)
    permission_classes = [IsAuthenticated]
    
    # ✅ File Upload ko lagi jaruri parser
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'profile', None) and getattr(user.profile, 'role', None)

        # Student: Aafno enrolled course ko note matra dekhne
        if role == 'student':
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return Note.objects.filter(course_id__in=enrolled_courses)
        
        # Admin/Teacher: Sabai dekhne
        return Note.objects.all()

    def get_permissions(self):
        """
        GET (View): Login vako jasle pani paayo (Student included).
        POST/DELETE (Edit): Admin ra Teacher le matra paayo.
        """
        if self.request.method in SAFE_METHODS: # GET, HEAD, OPTIONS
            return [IsAuthenticated()]
        
        # Write operations (POST, DELETE) ko lagi custom check
        return [IsAuthenticated(), IsAdminOrTeacher()]