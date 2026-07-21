    # # quiz/views.py
    # from rest_framework import generics, permissions, status
    # from rest_framework.response import Response
    # from rest_framework.views import APIView
    # from django.shortcuts import get_object_or_404

    # from .models import Quiz, Question, Choice, QuizSubmission
    # from .serializers import QuizSerializer, QuizAdminSerializer, QuizSubmissionSerializer
    # from courses.models import Enrollment


    # # ─── Permission Classes ───────────────────────────────────────────────────────

    # class IsTeacherOrAdmin(permissions.BasePermission):
    #     def has_permission(self, request, view):
    #         if not request.user.is_authenticated:
    #             return False
    #         role = getattr(getattr(request.user, 'profile', None), 'role', None)
    #         return role in ['teacher', 'admin'] or request.user.is_staff


    # # ─── Course Quiz List ─────────────────────────────────────────────────────────

    # class CourseQuizListView(generics.ListAPIView):
    #     serializer_class = QuizSerializer
    #     permission_classes = [permissions.IsAuthenticated]

    #     def get_queryset(self):
    #         course_id = self.kwargs['course_id']
    #         user = self.request.user
    #         role = getattr(getattr(user, 'profile', None), 'role', None)

    #         if role in ['teacher', 'admin'] or user.is_staff:
    #             return Quiz.objects.filter(course_id=course_id)

    #         is_enrolled = Enrollment.objects.filter(
    #             student=user,
    #             course_id=course_id
    #         ).exists()

    #         if is_enrolled:
    #             return Quiz.objects.filter(course_id=course_id)

    #         return Quiz.objects.none()


    # # ─── Quiz Detail ──────────────────────────────────────────────────────────────

    # class QuizDetailView(generics.RetrieveAPIView):
    #     serializer_class = QuizSerializer
    #     permission_classes = [permissions.IsAuthenticated]
    #     lookup_field = 'id'

    #     def get_queryset(self):
    #         user = self.request.user
    #         role = getattr(getattr(user, 'profile', None), 'role', None)

    #         if role in ['teacher', 'admin'] or user.is_staff:
    #             return Quiz.objects.all()

    #         enrolled_courses = Enrollment.objects.filter(
    #             student=user
    #         ).values_list('course', flat=True)

    #         return Quiz.objects.filter(course_id__in=enrolled_courses)


    # # ─── Quiz List + Create ───────────────────────────────────────────────────────

    # class QuizListCreateView(generics.ListCreateAPIView):
    #     queryset = Quiz.objects.all()

    #     # ✅ FIX: Admin le herda correct answers dekhauxa, student le hoina
    #     def get_serializer_class(self):
    #         user = self.request.user
    #         role = getattr(getattr(user, 'profile', None), 'role', None)
    #         if role in ['teacher', 'admin'] or user.is_staff:
    #             return QuizAdminSerializer
    #         return QuizSerializer

    #     def get_permissions(self):
    #         if self.request.method == 'POST':
    #             return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
    #         return [permissions.IsAuthenticated()]


    # # ─── Submit Quiz ──────────────────────────────────────────────────────────────

    # class SubmitQuizView(APIView):
    #     permission_classes = [permissions.IsAuthenticated]

    #     def post(self, request, quiz_id):
    #         user = request.user
    #         quiz = get_object_or_404(Quiz, id=quiz_id)

    #         user_answers = request.data.get('answers', {})

    #         if not user_answers:
    #             return Response(
    #                 {"error": "answers field required."},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         questions = quiz.questions.all()
    #         correct_count = 0

    #         for question in questions:
    #             selected_choice_id = user_answers.get(str(question.id))

    #             if selected_choice_id:
    #                 is_correct = Choice.objects.filter(
    #                     id=selected_choice_id,
    #                     question=question,
    #                     is_correct=True
    #                 ).exists()
    #                 if is_correct:
    #                     correct_count += 1

    #         total = questions.count()
    #         score_percentage = (correct_count / total * 100) if total > 0 else 0

    #         # ✅ Duplicate submission update garne, naya nagarne
    #         submission, created = QuizSubmission.objects.update_or_create(
    #             student=user,
    #             quiz=quiz,
    #             defaults={'score': score_percentage}
    #         )

    #         return Response({
    #             "score": round(score_percentage, 2),
    #             "correct_answers": correct_count,
    #             "total_questions": total,
    #             "passed": score_percentage >= 70
    #         }, status=status.HTTP_200_OK)


    # # ─── Student Dashboard ────────────────────────────────────────────────────────

    # class StudentDashboardView(APIView):
    #     permission_classes = [permissions.IsAuthenticated]

    #     def get(self, request):
    #         user = request.user
    #         submissions = QuizSubmission.objects.filter(
    #             student=user
    #         ).order_by('-submitted_at')

    #         last_submission = submissions.first()

    #         warning_message = None
    #         if last_submission and last_submission.score < 70:
    #             warning_message = "तिम्रो मेहेनत पुगिरहेको छैन, अझै मेहेनत गर्नुपर्छ!"

    #         return Response({
    #             "user": user.username,
    #             "warning_message": warning_message,
    #             "last_score": last_submission.score if last_submission else None,
    #             "total_quizzes_attempted": submissions.count(),
    #         })


    # # ─── Admin: Quiz Submissions List ────────────────────────────────────────────

    # class AdminQuizSubmissionsView(generics.ListAPIView):
    #     serializer_class = QuizSubmissionSerializer
    #     permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    #     def get_queryset(self):
    #         quiz_id = self.kwargs['quiz_id']
    #         get_object_or_404(Quiz, id=quiz_id)
    #         return QuizSubmission.objects.filter(
    #             quiz_id=quiz_id
    #         ).order_by('-submitted_at')


    # # ─── Student: My Submissions ──────────────────────────────────────────────────

    # class StudentSubmissionsView(generics.ListAPIView):
    #     serializer_class = QuizSubmissionSerializer
    #     permission_classes = [permissions.IsAuthenticated]

    #     def get_queryset(self):
    #         return QuizSubmission.objects.filter(
    #             student=self.request.user
    #         ).order_by('-submitted_at')
    from rest_framework import generics, permissions, status
    from rest_framework.response import Response
    from rest_framework.views import APIView
    from rest_framework.decorators import api_view, permission_classes
    from django.shortcuts import get_object_or_404
    from .models import Quiz, Question, Choice, QuizSubmission
    from .serializers import QuizSerializer, QuizAdminSerializer, QuizSubmissionSerializer
    from courses.models import Enrollment
    from notes.models import Note
    from google import genai
    from google.genai import types
    import json, os

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
            is_enrolled = Enrollment.objects.filter(student=user, course_id=course_id).exists()
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
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return Quiz.objects.filter(course_id__in=enrolled_courses)

    # ─── Quiz List + Create ───────────────────────────────────────────────────────
    class QuizListCreateView(generics.ListCreateAPIView):
        queryset = Quiz.objects.all()
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
                return Response({"error": "answers field required."}, status=status.HTTP_400_BAD_REQUEST)
            questions = quiz.questions.all()
            correct_count = 0
            for question in questions:
                selected_choice_id = user_answers.get(str(question.id))
                if selected_choice_id:
                    is_correct = Choice.objects.filter(
                        id=selected_choice_id, question=question, is_correct=True
                    ).exists()
                    if is_correct:
                        correct_count += 1
            total = questions.count()
            score_percentage = (correct_count / total * 100) if total > 0 else 0
            submission, created = QuizSubmission.objects.update_or_create(
                student=user, quiz=quiz, defaults={'score': score_percentage}
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
            submissions = QuizSubmission.objects.filter(student=user).order_by('-submitted_at')
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
            return QuizSubmission.objects.filter(quiz_id=quiz_id).order_by('-submitted_at')

    # ─── Student: My Submissions ──────────────────────────────────────────────────
    class StudentSubmissionsView(generics.ListAPIView):
        serializer_class = QuizSubmissionSerializer
        permission_classes = [permissions.IsAuthenticated]
        def get_queryset(self):
            return QuizSubmission.objects.filter(student=self.request.user).order_by('-submitted_at')

    # ─── AI Quiz Generator ────────────────────────────────────────────────────────
    API_KEY = os.environ.get('GEMINI_API_KEY')
    gemini_client = genai.Client(api_key=API_KEY)
    # @api_view(['POST'])
    # @permission_classes([permissions.IsAuthenticated])
    # def ai_generate_quiz(request):
    #     user = request.user
    #     role = getattr(getattr(user, 'profile', None), 'role', None)
    #     if role not in ['teacher', 'admin'] and not user.is_staff:
    #         return Response({'error': 'Permission denied'}, status=403)

    #     course_id = request.data.get('course_id')
    #     num_questions = int(request.data.get('num_questions', 5))
    #     topic_filter = request.data.get('topic', '')

    #     if not course_id:
    #         return Response({'error': 'course_id required'}, status=400)

    #     notes = Note.objects.filter(course_id=course_id, content__isnull=False).exclude(content='')
    #     if topic_filter:
    #         notes = notes.filter(title__icontains=topic_filter)
    #     if not notes.exists():
    #         return Response({'error': 'यो course मा कुनै notes छैन। पहिले notes upload गर्नुहोस्।'}, status=400)

    #     combined_content = ""
    #     for note in notes[:5]:
    #         content = note.content.strip()[:2000]
    #         combined_content += f"=== TOPIC: {note.title} ===\n{content}\n\n"

    #     prompt = f"""You are a quiz generator. Read the course notes below and create exactly {num_questions} multiple choice questions.

    # NOTES:
    # {combined_content}

    # Return ONLY valid JSON, no markdown, no explanation:
    # {{
    #   "quiz_title": "Quiz title here",
    #   "questions": [
    #     {{
    #       "text": "Question text here?",
    #       "options": [
    #         {{"text": "Option A", "is_correct": false}},
    #         {{"text": "Option B", "is_correct": true}},
    #         {{"text": "Option C", "is_correct": false}},
    #         {{"text": "Option D", "is_correct": false}}
    #       ]
    #     }}
    #   ]
    # }}

    # Rules:
    # - Exactly {num_questions} questions
    # - Each question has exactly 4 options
    # - Each question has exactly 1 correct answer
    # - Base questions on the notes content only
    # - Return pure JSON only"""

    #     try:
    #         response = gemini_client.models.generate_content(
    #             model='gemini-2.5-flash',
    #             contents=prompt,
    #             config=types.GenerateContentConfig(
    #                 max_output_tokens=2048,
    #                 temperature=0.7,
    #             )
    #         )
    #         raw = response.text.strip().replace('```json', '').replace('```', '').strip()
    #         data = json.loads(raw)
    #         return Response({'success': True, 'generated': data})

    #     except json.JSONDecodeError as e:
    #         print(f"JSON Parse Error: {e}")
    #         return Response({'error': 'AI le galat format diyo. Feri try garnuhos.'}, status=500)
    #     except Exception as e:
    #         print(f"AI Error: {type(e).__name__}: {e}")
    #         return Response({'error': str(e)}, status=500)
    @api_view(['POST'])
    @permission_classes([permissions.IsAuthenticated])
    def ai_generate_quiz(request):
        user = request.user
        role = getattr(getattr(user, 'profile', None), 'role', None)
        if role not in ['teacher', 'admin'] and not user.is_staff:
            return Response({'error': 'Permission denied'}, status=403)

        course_id = request.data.get('course_id')
        video_id = request.data.get('video_id')  # ✅ फ्रन्टइन्डबाट भिडियो/टपिकको ID लिने
        num_questions = int(request.data.get('num_questions', 5))
        topic_filter = request.data.get('topic', '')

        if not course_id:
            return Response({'error': 'course_id required'}, status=400)

        # ✅ नयाँ लजिक: यदि विशिष्ट भिडियो/टपिक सेलेक्ट छ भने त्यसकै नोट पहिले खोज्ने
        if video_id:
            notes = Note.objects.filter(video=video_id, content__isnull=False).exclude(content='')
        else:
            notes = Note.objects.filter(course_id=course_id, content__isnull=False).exclude(content='')

        # यदि टेक्स्ट फिल्टर पनि हालेको छ भने नामबाट फिल्टर गर्ने
        if topic_filter:
            notes = notes.filter(title__icontains=topic_filter)

        # यदि नोट भेटिएन भने युजरलाई जानकारी दिने
        if not notes.exists():
            return Response({'error': 'यो टपिक वा कोर्समा कुनै नोट भेटिएन। पहिले यस टपिकको नोट अपलोड गर्नुहोस्।'}, status=400)

        # नोटको टेक्स्ट मिलाउने
        combined_content = ""
        for note in notes[:5]:
            content = note.content.strip()[:2000]
            combined_content += f"=== TOPIC: {note.title} ===\n{content}\n\n"

        # Gemini Prompt (पुरानै)
        prompt = f"""You are a quiz generator. Read the course notes below and create exactly {num_questions} multiple choice questions.

    NOTES:
    {combined_content}

    Return ONLY valid JSON, no markdown, no explanation:
    {{
    "quiz_title": "Quiz title here",
    "questions": [
        {{
        "text": "Question text here?",
        "options": [
            {{"text": "Option A", "is_correct": false}},
            {{"text": "Option B", "is_correct": true}},
            {{"text": "Option C", "is_correct": false}},
            {{"text": "Option D", "is_correct": false}}
        ]
        }}
    ]
    }}

    Rules:
    - Exactly {num_questions} questions
    - Each question has exactly 4 options
    - Each question has exactly 1 correct answer
    - Base questions on the notes content only
    - Return pure JSON only"""

        try:
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    temperature=0.7,
                )
            )
            raw = response.text.strip().replace('```json', '').replace('```', '').strip()
            data = json.loads(raw)
            return Response({'success': True, 'generated': data})

        except json.JSONDecodeError as e:
            return Response({'error': 'AI le galat format diyo. Feri try garnuhos.'}, status=500)
        except Exception as e:
            return Response({'error': str(e)}, status=500)