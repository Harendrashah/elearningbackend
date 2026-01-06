from django.urls import path
from .views import InstructorListView

urlpatterns = [
    path('', InstructorListView.as_view()),
]
