from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from .permissions import IsInstructorOrAdmin

# --- COURSE VIEWSET (Jasta ko testai) ---
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.filter(is_published=True)
        
        role = getattr(user.profile, 'role', None) if hasattr(user, 'profile') else None
        if role in ['admin', 'teacher'] or user.is_staff:
            return Course.objects.all()
        return Course.objects.filter(is_published=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        if serializer.validated_data.get('instructor'):
            serializer.save()
        elif hasattr(user, 'instructor_profile'):
            serializer.save(instructor=user.instructor_profile)
        elif user.is_staff:
             serializer.save(instructor=None)
        else:
             raise ValidationError({"error": "You must be an instructor to create a course."})


# --- ENROLLMENT VIEWSET (Magic Fix Here) ---
class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, 'role', None) if hasattr(user, 'profile') else None
        if role == 'student':
            return Enrollment.objects.filter(student=user)
        return Enrollment.objects.all()

    # ✅ YO METHOD LE DATA MODIFIY GARXA (Main Fix)
    def create(self, request, *args, **kwargs):
        user = request.user
        
        # 1. Request Data lai Copy garne (Mutable banauna)
        # Yesle garda hami data vitra change garna sakxau
        data = request.data.copy()

        # 2. Yedi 'student' field aako xaina vane, Login user ko ID haldine
        if 'student' not in data:
            data['student'] = user.id  # <--- FORCE INJECT STUDENT ID

        # 3. Serializer lai modified data pathaune
        serializer = self.get_serializer(data=data)
        
        # 4. Check Validations
        if not serializer.is_valid():
            # Error log garne (Console ma herna sajilo hunxa)
            print("Enrollment Error:", serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 5. Duplicate Check (Logic inside View for safety)
        student_id = data['student']
        course_id = data.get('course')
        
        if Enrollment.objects.filter(student_id=student_id, course_id=course_id).exists():
            return Response(
                {"message": "You are already enrolled in this course."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 6. Save
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)