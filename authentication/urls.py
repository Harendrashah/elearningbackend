from django.urls import path
from . import views
from .views import AdminUserListView, AdminUserDetailView


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.UserProfileDetailView.as_view(), name='user-profile'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
]