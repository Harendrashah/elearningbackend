from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LiveClassViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'live-classes', LiveClassViewSet, basename='liveclass')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
