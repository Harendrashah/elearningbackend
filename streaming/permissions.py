from rest_framework.permissions import BasePermission

class IsInstructorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = getattr(request.user.profile, 'role', None)
        return role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        role = getattr(request.user.profile, 'role', None)
        if role == 'admin':
            return True
        if role == 'teacher':
            return obj.course.instructor.user == request.user
        return False
