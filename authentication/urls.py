#urls.py
from django.urls import path
from .views import (
    register_view,
    login_view,
    UserProfileDetailView,
    verify_otp
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),
    path('verify-otp/', verify_otp, name='verify-otp'),
]
