# quiz/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Quiz, Question, Choice, QuizSubmission
from .serializers import QuizSerializer, QuizAdminSerializer, QuizSubmissionSerializer
from courses.models import Enrollment


# ─── Permission Classes ───────────────────────────────────────────────────────

class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = getattr(getattr(request.user, 'profile', None), 'role', None)
        return role in ['teacher', 'admin'] or request.user.is_staff


# ─── Course Quiz List ─────────────────────────────────────────────────────────

class CourseQuizListView(generics.ListAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        user = self.request.user
        role = getattr(getattr(user, 'profile', None), 'role', None)

        if role in ['teacher', 'admin'] or user.is_staff:
            return Quiz.objects.filter(course_id=course_id)

        is_enrolled = Enrollment.objects.filter(
            student=user,
            course_id=course_id
        ).exists()

        if is_enrolled:
            return Quiz.objects.filter(course_id=course_id)

        return Quiz.objects.none()


# ─── Quiz Detail ──────────────────────────────────────────────────────────────

class QuizDetailView(generics.RetrieveAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        role = getattr(getattr(user, 'profile', None), 'role', None)

        if role in ['teacher', 'admin'] or user.is_staff:
            return Quiz.objects.all()

        enrolled_courses = Enrollment.objects.filter(
            student=user
        ).values_list('course', flat=True)

        return Quiz.objects.filter(course_id__in=enrolled_courses)


# ─── Quiz List + Create ───────────────────────────────────────────────────────

class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()

    # ✅ FIX: Admin le herda correct answers dekhauxa, student le hoina
    def get_serializer_class(self):
        user = self.request.user
        role = getattr(getattr(user, 'profile', None), 'role', None)
        if role in ['teacher', 'admin'] or user.is_staff:
            return QuizAdminSerializer
        return QuizSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]


# ─── Submit Quiz ──────────────────────────────────────────────────────────────

class SubmitQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        user = request.user
        quiz = get_object_or_404(Quiz, id=quiz_id)

        user_answers = request.data.get('answers', {})

        if not user_answers:
            return Response(
                {"error": "answers field required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        questions = quiz.questions.all()
        correct_count = 0

        for question in questions:
            selected_choice_id = user_answers.get(str(question.id))

            if selected_choice_id:
                is_correct = Choice.objects.filter(
                    id=selected_choice_id,
                    question=question,
                    is_correct=True
                ).exists()
                if is_correct:
                    correct_count += 1

        total = questions.count()
        score_percentage = (correct_count / total * 100) if total > 0 else 0

        # ✅ Duplicate submission update garne, naya nagarne
        submission, created = QuizSubmission.objects.update_or_create(
            student=user,
            quiz=quiz,
            defaults={'score': score_percentage}
        )

        return Response({
            "score": round(score_percentage, 2),
            "correct_answers": correct_count,
            "total_questions": total,
            "passed": score_percentage >= 70
        }, status=status.HTTP_200_OK)


# ─── Student Dashboard ────────────────────────────────────────────────────────

class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        submissions = QuizSubmission.objects.filter(
            student=user
        ).order_by('-submitted_at')

        last_submission = submissions.first()

        warning_message = None
        if last_submission and last_submission.score < 70:
            warning_message = "तिम्रो मेहेनत पुगिरहेको छैन, अझै मेहेनत गर्नुपर्छ!"

        return Response({
            "user": user.username,
            "warning_message": warning_message,
            "last_score": last_submission.score if last_submission else None,
            "total_quizzes_attempted": submissions.count(),
        })


# ─── Admin: Quiz Submissions List ────────────────────────────────────────────

class AdminQuizSubmissionsView(generics.ListAPIView):
    serializer_class = QuizSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        get_object_or_404(Quiz, id=quiz_id)
        return QuizSubmission.objects.filter(
            quiz_id=quiz_id
        ).order_by('-submitted_at')


# ─── Student: My Submissions ──────────────────────────────────────────────────

class StudentSubmissionsView(generics.ListAPIView):
    serializer_class = QuizSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizSubmission.objects.filter(
            student=self.request.user
        ).order_by('-submitted_at')