# instructors/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstructorViewSet

# Router create garne
router = DefaultRouter()
router.register(r'', InstructorViewSet, basename='instructors')

urlpatterns = [
    path('', include(router.urls)),
]