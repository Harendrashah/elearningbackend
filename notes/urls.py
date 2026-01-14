from rest_framework.routers import DefaultRouter
from .views import NoteViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('', NoteViewSet, basename='notes')

urlpatterns = [
    path('', include(router.urls)),
]
