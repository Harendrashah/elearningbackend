# authentication/permissions.py
from rest_framework import permissions

class IsAdminUserProfile(permissions.BasePermission):
    """
    Allow access only to users with role='admin'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.profile.role == 'admin')
