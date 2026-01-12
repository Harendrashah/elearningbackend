# authentication/permissions.py
from rest_framework import permissions

# Admin only
class IsAdminUserProfile(permissions.BasePermission):
    """
    Only admin can access.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.profile.role == 'admin')

# Teacher only
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.profile.role == 'teacher')

# Student only
class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.profile.role == 'student')
