from rest_framework.permissions import BasePermission

class IsInstructorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        profile = getattr(request.user, 'profile', None)
        role = getattr(profile, 'role', None)
        return role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        profile = getattr(request.user, 'profile', None)
        role = getattr(profile, 'role', None)

        if role == 'admin':
            return True

        if role == 'teacher':
            if hasattr(obj, 'instructor'):
                return obj.instructor == request.user
            if hasattr(obj, 'course'):
                return obj.course.instructor == request.user

        return False
