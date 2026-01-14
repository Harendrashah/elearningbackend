from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('courses.urls')),
    path('api/instructors/', include('instructors.urls')),
    path('api/streaming/', include('streaming.urls')),
    path('api/notes/', include('notes.urls')),   # ✅ Notes API
    

    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
