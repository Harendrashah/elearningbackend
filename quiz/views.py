from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Quiz
from .serializers import QuizSerializer
from courses.models import Enrollment 
from rest_framework.views import APIView
from .models import Quiz, Question, Choice, QuizSubmission
from .serializers import QuizSubmissionSerializer


class CourseQuizListView(generics.ListAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        user = self.request.user
        
        # Check if student is enrolled in this course
        is_enrolled = Enrollment.objects.filter(user=user, course_id=course_id).exists()
        
        if is_enrolled or user.profile.role in ['teacher', 'admin']:
            return Quiz.objects.filter(course_id=course_id)
        else:
            return Quiz.objects.none() # Enroll छैन भने खाली पठाइदिने

class QuizDetailView(generics.RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'



# views.py भित्रको SubmitQuizView परिमार्जन
class SubmitQuizView(APIView):
    def post(self, request, quiz_id):
        user = request.user
        # फ्रन्टइन्डबाट {0: choice_id, 1: choice_id} यसरी डेटा आउँछ
        user_answers = request.data.get('answers') 
        
        quiz = Quiz.objects.get(id=quiz_id)
        questions = quiz.questions.all()
        correct_count = 0

        # ब्याकइन्डमै सही उत्तर चेक गर्ने (चिटिङ रोक्न)
        for idx, question in enumerate(questions):
            selected_choice_id = user_answers.get(str(idx)) # Index को आधारमा
            if selected_choice_id:
                is_correct = Choice.objects.filter(
                    id=selected_choice_id, 
                    question=question, 
                    is_correct=True
                ).exists()
                if is_correct:
                    correct_count += 1
        
        score_percentage = (correct_count / questions.count()) * 100 if questions.count() > 0 else 0
        
        # Result Store गर्ने
        QuizSubmission.objects.create(
            student=user,
            quiz=quiz,
            score=score_percentage
        )

        return Response({
            "score": score_percentage,
            "correct_answers": correct_count,
            "total_questions": questions.count()
        })
class StudentDashboardView(APIView):
    def get(self, request):
        user = request.user
        # पछिल्लो क्विज सबमिसन तान्ने
        last_submission = QuizSubmission.objects.filter(student=user).order_by('-submitted_at').first()
        
        warning_message = None
        if last_submission and last_submission.score < 70:
            warning_message = "तिम्रो मेहेनत पुगिरहेको छैन, अझै मेहेनत गर्नुपर्छ!"

        return Response({
            "user": user.username,
            "warning_message": warning_message,
            "last_score": last_submission.score if last_submission else None
        })
class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class AdminQuizSubmissionsView(generics.ListAPIView):
    serializer_class = QuizSubmissionSerializer
    
    def get_queryset(self):
        # यो क्विजमा कस-कसले एक्जाम दियो भनेर पठाउने
        quiz_id = self.kwargs['quiz_id']
        return QuizSubmission.objects.filter(quiz_id=quiz_id).order_by('-submitted_at')

# views.py को सबैभन्दा तल यो थप्नुहोस्
class StudentSubmissionsView(generics.ListAPIView):
    serializer_class = QuizSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # लगइन भएको विद्यार्थीको मात्रै सबमिसन पठाउने
        return QuizSubmission.objects.filter(student=self.request.user).order_by('-submitted_at')