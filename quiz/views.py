# quiz/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

from django.shortcuts import get_object_or_404

from .models import Quiz, Question, Choice, QuizSubmission
from .serializers import (
    QuizSerializer,
    QuizAdminSerializer,
    QuizSubmissionSerializer,
)

from courses.models import Enrollment
from notes.models import Note

from google import genai
from google.genai import types

import json
import os


# ─── Permission Classes ───────────────────────────────────────────────────────

class IsTeacherOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        role = getattr(
            getattr(request.user, 'profile', None),
            'role',
            None
        )

        return (
            role in ['teacher', 'admin']
            or request.user.is_staff
        )


# ─── Course Quiz List ─────────────────────────────────────────────────────────

class CourseQuizListView(generics.ListAPIView):

    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        course_id = self.kwargs['course_id']
        user = self.request.user

        role = getattr(
            getattr(user, 'profile', None),
            'role',
            None
        )

        # Teacher / Admin / Staff can see all quizzes
        if role in ['teacher', 'admin'] or user.is_staff:
            return Quiz.objects.filter(
                course_id=course_id
            )

        # Student must be enrolled
        is_enrolled = Enrollment.objects.filter(
            student=user,
            course_id=course_id
        ).exists()

        if is_enrolled:
            return Quiz.objects.filter(
                course_id=course_id
            )

        return Quiz.objects.none()


# ─── Quiz Detail ──────────────────────────────────────────────────────────────

class QuizDetailView(generics.RetrieveAPIView):

    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = 'id'

    def get_queryset(self):

        user = self.request.user

        role = getattr(
            getattr(user, 'profile', None),
            'role',
            None
        )

        # Teacher / Admin / Staff can access all quizzes
        if role in ['teacher', 'admin'] or user.is_staff:
            return Quiz.objects.all()

        # Students can only access quizzes
        # from courses they are enrolled in
        enrolled_courses = Enrollment.objects.filter(
            student=user
        ).values_list(
            'course',
            flat=True
        )

        return Quiz.objects.filter(
            course_id__in=enrolled_courses
        )


# ─── Quiz List + Create ───────────────────────────────────────────────────────

class QuizListCreateView(generics.ListCreateAPIView):

    queryset = Quiz.objects.all()

    def get_serializer_class(self):

        user = self.request.user

        role = getattr(
            getattr(user, 'profile', None),
            'role',
            None
        )

        # Admin / Teacher gets correct answers
        if role in ['teacher', 'admin'] or user.is_staff:
            return QuizAdminSerializer

        # Student does not get correct answers
        return QuizSerializer

    def get_permissions(self):

        # Only Teacher / Admin can create quiz
        if self.request.method == 'POST':
            return [
                permissions.IsAuthenticated(),
                IsTeacherOrAdmin()
            ]

        return [
            permissions.IsAuthenticated()
        ]


# ─── Submit Quiz ──────────────────────────────────────────────────────────────

class SubmitQuizView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request, quiz_id):

        user = request.user

        quiz = get_object_or_404(
            Quiz,
            id=quiz_id
        )

        user_answers = request.data.get(
            'answers',
            {}
        )

        if not user_answers:

            return Response(
                {
                    "error": "answers field required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        questions = quiz.questions.all()

        correct_count = 0

        for question in questions:

            selected_choice_id = user_answers.get(
                str(question.id)
            )

            if selected_choice_id:

                is_correct = Choice.objects.filter(
                    id=selected_choice_id,
                    question=question,
                    is_correct=True
                ).exists()

                if is_correct:
                    correct_count += 1

        total = questions.count()

        score_percentage = (
            correct_count / total * 100
        ) if total > 0 else 0

        # Update existing submission
        # instead of creating duplicate submission
        submission, created = QuizSubmission.objects.update_or_create(
            student=user,
            quiz=quiz,
            defaults={
                'score': score_percentage
            }
        )

        return Response(
            {
                "score": round(
                    score_percentage,
                    2
                ),
                "correct_answers": correct_count,
                "total_questions": total,
                "passed": score_percentage >= 70
            },
            status=status.HTTP_200_OK
        )


# ─── Student Dashboard ───────────────────────────────────────────────────────

class StudentDashboardView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):

        user = request.user

        submissions = QuizSubmission.objects.filter(
            student=user
        ).order_by(
            '-submitted_at'
        )

        last_submission = submissions.first()

        warning_message = None

        if (
            last_submission
            and last_submission.score < 70
        ):

            warning_message = (
                "तिम्रो मेहेनत पुगिरहेको छैन, "
                "अझै मेहेनत गर्नुपर्छ!"
            )

        return Response(
            {
                "user": user.username,

                "warning_message": warning_message,

                "last_score": (
                    last_submission.score
                    if last_submission
                    else None
                ),

                "total_quizzes_attempted": (
                    submissions.count()
                ),
            }
        )


# ─── Admin: Quiz Submissions List ────────────────────────────────────────────

class AdminQuizSubmissionsView(generics.ListAPIView):

    serializer_class = QuizSubmissionSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsTeacherOrAdmin
    ]

    def get_queryset(self):

        quiz_id = self.kwargs['quiz_id']

        # Check quiz exists
        get_object_or_404(
            Quiz,
            id=quiz_id
        )

        return QuizSubmission.objects.filter(
            quiz_id=quiz_id
        ).order_by(
            '-submitted_at'
        )


# ─── Student: My Submissions ──────────────────────────────────────────────────

class StudentSubmissionsView(generics.ListAPIView):

    serializer_class = QuizSubmissionSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        return QuizSubmission.objects.filter(
            student=self.request.user
        ).order_by(
            '-submitted_at'
        )


# ─── AI Quiz Generator ────────────────────────────────────────────────────────

API_KEY = os.environ.get(
    'GEMINI_API_KEY'
)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing"
    )

# Gemini Client
client = genai.Client(
    api_key=API_KEY
)


@api_view(['POST'])
@permission_classes([
    permissions.IsAuthenticated
])
def ai_generate_quiz(request):

    user = request.user

    # Get user role
    role = getattr(
        getattr(user, 'profile', None),
        'role',
        None
    )

    # Only Teacher / Admin / Staff
    # can generate AI quizzes
    if (
        role not in ['teacher', 'admin']
        and not user.is_staff
    ):

        return Response(
            {
                'error': 'Permission denied'
            },
            status=status.HTTP_403_FORBIDDEN
        )


    # ─── Get Request Data ──────────────────────────────────────────────────────

    course_id = request.data.get(
        'course_id'
    )

    video_id = request.data.get(
        'video_id'
    )

    topic_filter = request.data.get(
        'topic',
        ''
    )

    try:

        num_questions = int(
            request.data.get(
                'num_questions',
                5
            )
        )

    except (TypeError, ValueError):

        return Response(
            {
                'error': 'num_questions must be a valid number'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    # ─── Validate Number of Questions ──────────────────────────────────────────

    if num_questions < 1:

        return Response(
            {
                'error': 'num_questions must be at least 1'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if num_questions > 20:

        return Response(
            {
                'error': 'Maximum 20 questions allowed'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    # ─── Validate Course ───────────────────────────────────────────────────────

    if not course_id:

        return Response(
            {
                'error': 'course_id required'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    # ─── Get Notes ─────────────────────────────────────────────────────────────

    # If a specific video/topic is selected,
    # get notes only from that video
    if video_id:

        notes = Note.objects.filter(
            video_id=video_id,
            content__isnull=False
        ).exclude(
            content=''
        )

    # Otherwise get notes from entire course
    else:

        notes = Note.objects.filter(
            course_id=course_id,
            content__isnull=False
        ).exclude(
            content=''
        )


    # ─── Topic Filter ──────────────────────────────────────────────────────────

    if topic_filter:

        notes = notes.filter(
            title__icontains=topic_filter
        )


    # ─── Check Notes ───────────────────────────────────────────────────────────

    if not notes.exists():

        return Response(
            {
                'error': (
                    'यो टपिक वा कोर्समा कुनै नोट भेटिएन। '
                    'पहिले यस टपिकको नोट अपलोड गर्नुहोस्।'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    # ─── Combine Notes ─────────────────────────────────────────────────────────

    combined_content = ""

    for note in notes[:5]:

        content = (
            note.content.strip()[:2000]
        )

        combined_content += (
            f"=== TOPIC: {note.title} ===\n"
            f"{content}\n\n"
        )


    # ─── Gemini Prompt ─────────────────────────────────────────────────────────

    prompt = f"""
You are an educational quiz generator.

Read the course notes below and create exactly
{num_questions} multiple choice questions.

NOTES:
{combined_content}

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add any explanation.

Required JSON format:

{{
    "quiz_title": "Quiz title here",
    "questions": [
        {{
            "text": "Question text here?",
            "options": [
                {{
                    "text": "Option A",
                    "is_correct": false
                }},
                {{
                    "text": "Option B",
                    "is_correct": true
                }},
                {{
                    "text": "Option C",
                    "is_correct": false
                }},
                {{
                    "text": "Option D",
                    "is_correct": false
                }}
            ]
        }}
    ]
}}

Rules:

- Create exactly {num_questions} questions.
- Each question must have exactly 4 options.
- Each question must have exactly 1 correct answer.
- The correct answer must have "is_correct": true.
- All other answers must have "is_correct": false.
- Questions must be based ONLY on the provided notes.
- Do not add information that is not present in the notes.
- Return pure JSON only.
"""


    # ─── Generate Quiz Using Gemini ────────────────────────────────────────────

    try:

        response = client.models.generate_content(

            model='gemini-2.5-flash',

            contents=prompt,

            config=types.GenerateContentConfig(

                max_output_tokens=4096,

                temperature=0.7,

            )
        )


        # ─── Get AI Response ───────────────────────────────────────────────────

        raw = response.text.strip()


        # Remove Markdown Code Block
        if raw.startswith(
            '```json'
        ):

            raw = raw[
                len('```json'):
            ]

        elif raw.startswith(
            '```'
        ):

            raw = raw[
                len('```'):
            ]


        if raw.endswith(
            '```'
        ):

            raw = raw[
                :-len('```')
            ]


        raw = raw.strip()


        # ─── Parse JSON ────────────────────────────────────────────────────────

        data = json.loads(
            raw
        )


        # ─── Validate Generated Data ───────────────────────────────────────────

        if 'questions' not in data:

            return Response(
                {
                    'error': (
                        'AI response does not contain questions.'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        if len(
            data['questions']
        ) != num_questions:

            return Response(
                {
                    'error': (
                        f'AI generated '
                        f'{len(data["questions"])} questions '
                        f'instead of {num_questions}.'
                    ),
                    'generated': data
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        # Validate each question
        for question in data['questions']:

            if 'text' not in question:

                return Response(
                    {
                        'error': (
                            'Generated question is missing text.'
                        )
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


            if (
                'options' not in question
                or len(question['options']) != 4
            ):

                return Response(
                    {
                        'error': (
                            'Each question must have '
                            'exactly 4 options.'
                        )
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


            correct_options = [
                option
                for option in question['options']
                if option.get(
                    'is_correct',
                    False
                )
            ]


            if len(
                correct_options
            ) != 1:

                return Response(
                    {
                        'error': (
                            'Each question must have '
                            'exactly 1 correct answer.'
                        )
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


        # ─── Success ───────────────────────────────────────────────────────────

        return Response(
            {
                'success': True,
                'generated': data
            },
            status=status.HTTP_200_OK
        )


    # ─── JSON Error ────────────────────────────────────────────────────────────

    except json.JSONDecodeError as e:

        print(
            f"JSON Parse Error: {e}"
        )

        return Response(
            {
                'error': (
                    'AI le galat format diyo. '
                    'Feri try garnuhos.'
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    # ─── Gemini / Other Error ──────────────────────────────────────────────────

    except Exception as e:

        print(
            f"AI Error: {type(e).__name__}: {e}"
        )

        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )