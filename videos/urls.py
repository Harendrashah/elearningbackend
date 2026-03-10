from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet

router = DefaultRouter()

# 👇 यहाँ 'basename' थप्नुपर्छ
router.register(r'videos', VideoViewSet, basename='video') 

urlpatterns = [
    path('', include(router.urls)),
]