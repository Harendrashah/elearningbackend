from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet

router = DefaultRouter()
router.register(r'videos', VideoViewSet) # URL: /api/videos/

urlpatterns = [
    path('', include(router.urls)),
]