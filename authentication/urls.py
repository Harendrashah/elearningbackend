from django.urls import path
from .views import (
    register_view,
    login_view,
    verify_otp,
    UserProfileDetailView,
    AdminUserListView,
    AdminUserDetailView
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('verify-otp/', verify_otp, name='verify-otp'),
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),

    # 🔥 ADMIN APIs
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
]
