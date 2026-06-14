# from django.urls import path
# from . import views

# urlpatterns = [
#     # 👇 यो लाइन थपिएको हो! यसले /api/quiz/ मा POST (सेभ) गर्न दिन्छ 👇
#     path('', views.QuizListCreateView.as_view(), name='quiz-list-create'),
#     path('submissions/', views.StudentSubmissionsView.as_view(), name='student-submissions'),

#     # कोर्सको ID पठाउँदा त्यो कोर्सको सबै क्विज आउँछ
#     path('courses/<int:course_id>/quizzes/', views.CourseQuizListView.as_view(), name='course-quizzes'),
    
#     # क्विजको ID पठाउँदा क्विज र त्यसका प्रश्नहरू आउँछ
#     path('quizzes/<int:id>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    
#     # क्विज सबमिट गर्नको लागि
#     path('quizzes/<int:quiz_id>/submit/', views.SubmitQuizView.as_view(), name='quiz-submit'),
    
#     # स्टुडेन्ट ड्यासबोर्ड (स्कोर र मेसेज देखाउन)
#     path('dashboard/', views.StudentDashboardView.as_view(), name='student-dashboard'),
#     path('quizzes/<int:quiz_id>/submissions/', views.AdminQuizSubmissionsView.as_view(), name='quiz-submissions-admin'),
# ]
# quiz/urls.py — यो पूरै replace गर्नुहोस्
from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuizListCreateView.as_view(), name='quiz-list-create'),
    path('submissions/', views.StudentSubmissionsView.as_view(), name='student-submissions'),
    path('courses/<int:course_id>/quizzes/', views.CourseQuizListView.as_view(), name='course-quizzes'),
    path('quizzes/<int:id>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:quiz_id>/submit/', views.SubmitQuizView.as_view(), name='quiz-submit'),
    path('dashboard/', views.StudentDashboardView.as_view(), name='student-dashboard'),
    path('quizzes/<int:quiz_id>/submissions/', views.AdminQuizSubmissionsView.as_view(), name='quiz-submissions-admin'),
    
    # ✅ नयाँ AI endpoint
    path('ai-generate/', views.ai_generate_quiz, name='ai-generate-quiz'),
]