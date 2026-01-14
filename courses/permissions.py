from rest_framework import permissions

class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Only admin or teacher can create/update/delete.
    Teacher can edit only own course.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Safe way to get role (avoids crash if profile doesn't exist)
        profile = getattr(request.user, 'profile', None)
        role = getattr(profile, 'role', None)
        
        return role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        profile = getattr(request.user, 'profile', None)
        role = getattr(profile, 'role', None)

        if role == 'admin':
            return True
        
        if role == 'teacher':
            # Check if the teacher is the instructor of the course
            return getattr(obj, 'instructor', None) == request.user
            
        return False