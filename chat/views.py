from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os

from google import genai
from google.genai import types

from courses.models import Course, Enrollment
from notes.models import Note

API_KEY = os.environ.get('GEMINI_API_KEY')

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing")

# Gemini Client
client = genai.Client(
    api_key=API_KEY
)

# ✅ Correct model names for the new SDK (no "models/" prefix needed)
MODELS_TO_TRY = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
]


def get_enrolled_notes_context(user):
    context_parts = []
    enrolled_course_names = []

    enrollments = Enrollment.objects.filter(student=user).select_related('course')
    if not enrollments.exists():
        return None, []

    for enrollment in enrollments:
        course = enrollment.course
        enrolled_course_names.append(course.title)
        for note in Note.objects.filter(course=course):
            content = (note.content or '').strip()
            if content:
                truncated = content[:3000] if len(content) > 3000 else content
                context_parts.append(
                    f"=== COURSE: {course.title} | TOPIC: {note.title} ===\n{truncated}\n"
                )

    return ("\n".join(context_parts) if context_parts else None), enrolled_course_names


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_api(request):
    user_message = request.data.get('message', '').strip()
    if not user_message:
        return Response({'response': 'Please ask a question.'})

    user = request.user

    courses_list = "\n".join(
        [f"- {c.title} (Rs. {c.price})" for c in Course.objects.filter(is_published=True)]
    ) or "No courses are available."

    notes_context, enrolled_courses = get_enrolled_notes_context(user)
    has_notes = bool(notes_context)

    print(f"\n{'='*50}")
    print(f"USER: {getattr(user, 'email', user.username)}")
    print(f"ENROLLED: {enrolled_courses} | NOTES: {has_notes}")
    print(f"QUESTION: {user_message}")
    print(f"{'='*50}\n")

    system_prompt = f"""
You are 'Informatics AI' — a smart e-learning assistant.

**LANGUAGE RULE:**
- If asked in Nepali → reply in Nepali (Devanagari)
- If asked in English → reply in English
- If mixed → reply in whichever language is more dominant
- Do not translate technical terms (HTML, VLAN, Python, etc.)

**PLATFORM COURSES:**
{courses_list}

**STUDENT NOTES (from {getattr(user, 'username', 'Student')}'s enrolled courses):**
{notes_context if has_notes else "This student hasn't enrolled in any course yet."}

**RULES:**
- If the notes contain the answer → explain from the notes
- If not in the notes but enrolled → answer from general knowledge
- If not enrolled → mention the courses and encourage enrollment
- Code examples → put in a code block
- Short question → short answer, complex → structured answer
""".strip()

    bot_reply = None
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=1024,
                    temperature=0.7,
                )
            )
            bot_reply = response.text or "Sorry, couldn't generate a response."
            print(f"✅ Model used: {model_name}")
            break
        except Exception as e:
            print(f"⚠️ {model_name} failed: {type(e).__name__}: {e}")
            continue

    if not bot_reply:
        bot_reply = "AI quota exhausted. Please try again in a while."

    return Response({'response': bot_reply})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_status(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    enrolled_courses = [
        {
            'id': e.course.id,
            'title': e.course.title,
            'has_notes': Note.objects.filter(
                course=e.course, content__isnull=False
            ).exclude(content='').exists()
        }
        for e in enrollments
    ]
    return Response({
        'is_enrolled': bool(enrolled_courses),
        'enrolled_courses': enrolled_courses,
        'total_courses': len(enrolled_courses)
    })