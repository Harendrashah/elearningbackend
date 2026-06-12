from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.chatbot_api, name='chatbot_api'),
    path('status/', views.chat_status, name='chat_status'),  # ← यो थपिएको हो
]