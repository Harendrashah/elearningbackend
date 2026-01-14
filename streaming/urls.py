from rest_framework.routers import DefaultRouter
from .views import LiveSessionViewSet

router = DefaultRouter()
router.register('live-sessions', LiveSessionViewSet, basename='live-sessions')

urlpatterns = router.urls
