# authentication/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_role',
        'is_staff',
        'is_active',
    )
    list_select_related = ('profile',)

    def get_role(self, obj):
        return obj.profile.role
    get_role.short_description = 'Role'


# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'is_verified')
    search_fields = ('user__username', 'phone', 'role')
    list_filter = ('role', 'is_verified')
