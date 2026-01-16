from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from .permissions import IsInstructorOrAdmin

# --- COURSE VIEWSET ---
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    # Default: Login vako le matra herna paune (Public le GET matra)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        # 1. Unauthenticated users see only published courses
        if not user.is_authenticated:
            return Course.objects.filter(is_published=True)

        # 2. Check role safely
        role = getattr(user.profile, 'role', None) if hasattr(user, 'profile') else None

        # 3. Admin/Teacher sees all
        if role in ['admin', 'teacher'] or user.is_staff:
            return Course.objects.all()

        # 4. Student sees only published
        return Course.objects.filter(is_published=True)

    def get_permissions(self):
        # Create/Edit/Delete: Only Instructor or Admin
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        
        # A. Admin le Frontend bata 'instructor' select gareko xa vane
        if serializer.validated_data.get('instructor'):
            serializer.save()
            return

        # B. Logged-in Teacher ho vane -> Aafai Instructor hune
        if hasattr(user, 'instructor_profile'):
            serializer.save(instructor=user.instructor_profile)
        
        # C. Admin le select garena vane -> NULL allow garne
        elif user.is_staff:
             serializer.save(instructor=None)
        
        # D. Student le hack garna khojyo vane -> Error
        else:
             raise ValidationError({"error": "You must be an instructor to create a course."})


# --- ENROLLMENT VIEWSET ---
class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, 'role', None) if hasattr(user, 'profile') else None

        # Student: See ONLY my enrollments
        if role == 'student':
            return Enrollment.objects.filter(student=user)
        
        # Admin/Teacher: See ALL enrollments
        return Enrollment.objects.all()

    # ✅ YO CREATE METHOD LE DUPLICATE ENROLLMENT ROKXA
    def create(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course')

        if not course_id:
            return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already enrolled
        if Enrollment.objects.filter(student=user, course_id=course_id).exists():
            return Response(
                {"message": "You are already enrolled in this course."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Proceed to create
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        
        # ✅ FIX: Yadi Admin le data pathako xa vane, tehi use garne
        # Natra matra login user (student) lai use garne
        if user.is_staff and 'student' in self.request.data:
            serializer.save()  # Serializer le frontend bata aako ID linxa
        else:
            serializer.save(student=user) # Student aafai enroll hunda