# courses/permissions.py
from rest_framework import permissions

class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Only Admin or Teacher can create/update/delete.
    Teacher can edit ONLY their own course.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Profile check (errors avoid garna getattr use gareko)
        profile = getattr(request.user, 'profile', None)
        role = getattr(profile, 'role', None)
        
        return role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        # Admin lai sabai power
        if request.user.is_staff or request.user.is_superuser:
            return True

        profile = getattr(request.user, 'profile', None)
        role = getattr(profile, 'role', None)

        if role == 'admin':
            return True
        
        if role == 'teacher':
            # ✅ FIX: Check if course's instructor USER matches request USER
            # obj.instructor is an Instructor Instance, so we check obj.instructor.user
            if obj.instructor and obj.instructor.user == request.user:
                return True
            
        return False