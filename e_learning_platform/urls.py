# e_learning_platform/urls.py

from django.contrib import admin
from django.urls import path, include

# 1. Import the new view we just created
from . import views

urlpatterns = [
    # 2. Add this new path for the root URL
    path('', views.api_root, name='api-root'),
    
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
]

# ... (rest of the file)