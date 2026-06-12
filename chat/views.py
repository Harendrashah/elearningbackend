from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os

from google import genai
from google.genai import types

from courses.models import Course, Enrollment
from notes.models import Note

API_KEY = 'AQ.Ab8RN6LdO2HpRSxjZVJZ94_KvmVEDTZt0t4nteykSp9qBwIYmg'
client = genai.Client(api_key=API_KEY)

# ✅ नयाँ SDK मा सही model names (prefix "models/" नचाहिने)
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
        return Response({'response': 'कृपया प्रश्न सोध्नुहोस्।'})

    user = request.user

    courses_list = "\n".join(
        [f"- {c.title} (Rs. {c.price})" for c in Course.objects.filter(is_published=True)]
    ) or "कुनै course उपलब्ध छैन।"

    notes_context, enrolled_courses = get_enrolled_notes_context(user)
    has_notes = bool(notes_context)

    print(f"\n{'='*50}")
    print(f"USER: {getattr(user, 'email', user.username)}")
    print(f"ENROLLED: {enrolled_courses} | NOTES: {has_notes}")
    print(f"QUESTION: {user_message}")
    print(f"{'='*50}\n")

    system_prompt = f"""
तपाईं 'Informatics AI' हुनुहुन्छ — एउटा smart e-learning assistant।

**LANGUAGE RULE:**
- Nepali मा सोधे → Nepali (Devanagari) मा जवाफ दिनुहोस्
- English मा सोधे → English मा जवाफ दिनुहोस्
- Mixed भए → जुन बढी छ त्यही भाषामा
- Technical terms (HTML, VLAN, Python, etc.) translate नगर्नुहोस्

**PLATFORM COURSES:**
{courses_list}

**STUDENT NOTES ({getattr(user, 'username', 'Student')} को enrolled courses बाट):**
{notes_context if has_notes else "यो student ले अहिलेसम्म कुनै course enroll गरेको छैन।"}

**RULES:**
- Notes मा answer छ भने → notes बाट explain गर्नुहोस्
- Notes मा छैन तर enrolled छ → general knowledge बाट answer दिनुहोस्
- Enrolled छैन → courses बताउनुहोस् र enroll गर्न encourage गर्नुहोस्
- Code examples → code block मा राख्नुहोस्
- छोटो प्रश्न → छोटो answer, complex → structured answer
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
            bot_reply = response.text or "माफ गर्नुहोला, जवाफ generate हुन सकेन।"
            print(f"✅ Model used: {model_name}")
            break
        except Exception as e:
            print(f"⚠️ {model_name} failed: {type(e).__name__}: {e}")
            continue

    if not bot_reply:
        bot_reply = "AI को quota सकियो। केहि समय पछि फेरि प्रयास गर्नुहोस्।"

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