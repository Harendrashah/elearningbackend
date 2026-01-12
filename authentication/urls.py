from django.urls import path
from .views import (
    register_view,
    login_view,
    verify_otp,
    UserProfileDetailView,
    AdminUserListView,
    AdminUserDetailView
)
from .views import (
    TeacherStudentListView,
    TeacherStudentDetailView,
    teacher_dashboard_stats,
    enroll_student
)


urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('verify-otp/', verify_otp, name='verify-otp'),
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),

    # 🔥 ADMIN APIs
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    
    # teacher APIs
    path('teacher/students/', TeacherStudentListView.as_view(), name='teacher-student-list'),
    path('teacher/students/<int:id>/', TeacherStudentDetailView.as_view(), name='teacher-student-detail'),
    path('teacher/dashboard/', teacher_dashboard_stats, name='teacher-dashboard'),
    path('teacher/enroll/', enroll_student, name='teacher-enroll-student'),
]
