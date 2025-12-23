from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, ContentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

content_list = ContentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
content_detail = ContentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', include(router.urls)),
    path('courses/<int:course_pk>/contents/', content_list, name='course-contents'),
    path('courses/<int:course_pk>/contents/<int:pk>/', content_detail, name='course-content-detail'),
]
