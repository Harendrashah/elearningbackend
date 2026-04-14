# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# import google.generativeai as genai

# # --- MODELS IMPORTS ---
# from courses.models import Course, Enrollment
# from notes.models import Note
# try:
#     from streaming.models import Stream 
#     from videos.models import Video      
# except ImportError:
#     pass

# # तपाईंको API KEY
# API_KEY = "AIzaSyDhnjNrcIOxMXKY-_bjw9aGVOanN_w0kIE"
# genai.configure(api_key=API_KEY)

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def chatbot_api(request):
#     user_message = request.data.get('message', '')
#     user = request.user 
    
#     courses_info = ""
#     enrolled_notes_context = ""

#     # कोर्स इन्फो
#     all_courses = Course.objects.all()
#     for course in all_courses:
#         courses_info += f"- {course.title}: Rs. {course.price}\n"

#     # युजर इनरोलमेन्ट र नोट चेक
#     if user.is_authenticated:
#         # यहाँ 'student=user' लाई आफ्नो मोडल अनुसार 'user=user' मा फेर्नु पर्ने हुन सक्छ
#         enrollments = Enrollment.objects.filter(student=user) 
#         if enrollments.exists():
#             for enc in enrollments:
#                 notes = Note.objects.filter(course=enc.course)
#                 for note in notes:
#                     if note.content: # यदि कन्टेन्ट छ भने मात्रै थप्ने
#                         enrolled_notes_context += f"TOPIC: {note.title}\nCONTENT: {note.content}\n\n"

#     system_instruction = f"""
#     You are Informatics AI. 
#     DATABASE INFO: {courses_info}
#     USER NOTES: {enrolled_notes_context if enrolled_notes_context else "NONE"}

#     RULE: If USER NOTES has information, you MUST provide it directly. 
#     Do NOT tell them to enroll if they are already enrolled.
#     """
#     # ४. AI Response
#     try:
#         model = genai.GenerativeModel('gemini-flash-latest')
#         full_prompt = f"{system_instruction}\n\nUser Question: {user_message}"
#         response = model.generate_content(full_prompt)
#         bot_reply = response.text if response.text else "माफ गर्नुहोला, मैले बुझ्न सकिन।"
#     except Exception as e:
#         print(f"Gemini Error: {e}")
#         bot_reply = "सिस्टममा समस्या आयो। कृपया फेरि प्रयास गर्नुहोला।"

#     return Response({'response': bot_reply})
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import google.generativeai as genai

# --- MODELS IMPORTS ---
# तपाईंको एपको नाम अनुसार 'courses' र 'notes' बाट इम्पोर्ट गर्नुहोस्
from courses.models import Course, Enrollment
from notes.models import Note

try:
    from streaming.models import Stream 
    from videos.models import Video      
except ImportError:
    pass

# तपाईंको Gemini API KEY
API_KEY = "AIzaSyDhnjNrcIOxMXKY-_bjw9aGVOanN_w0kIE"
genai.configure(api_key=API_KEY)

@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_api(request):
    user_message = request.data.get('message', '')
    user = request.user 
    
    courses_info = ""
    enrolled_notes_context = ""

    # 1. सबै कोर्षको जानकारी तान्ने
    all_courses = Course.objects.all()
    for course in all_courses:
        courses_info += f"- {course.title}: Rs. {course.price}\n"

    # 2. युजर इनरोलमेन्ट र नोट तान्ने
    if user.is_authenticated:
        user_enrollments = Enrollment.objects.filter(student=user)
        
        if user_enrollments.exists():
            enrolled_notes_context = "\n--- PRIVATE NOTES FOR THIS STUDENT ---\n"
            for enrollment in user_enrollments:
                course_notes = Note.objects.filter(course=enrollment.course)
                for note in course_notes:
                    # नोटको सामाग्री (Content) छ भने मात्र थप्ने
                    content_text = note.content if note.content else "No text description available."
                    enrolled_notes_context += f"TOPIC: {note.title}\nCONTENT: {content_text}\n\n"

    # >>> ३. अब यहाँ डिबग प्रिन्ट राख्नुहोस् (डेटा तानेपछि) <<<
    print(f"\n--- FINAL DEBUG LOGS ---")
    print(f"USER: {user} | AUTH: {user.is_authenticated}")
    if user.is_authenticated:
        print(f"ENROLLMENT COUNT: {Enrollment.objects.filter(student=user).count()}")
        print(f"CONTEXT FOUND: {'YES' if enrolled_notes_context.strip() else 'NO'}")
        print(f"CONTEXT PREVIEW: {enrolled_notes_context[:100]}...")
    print(f"--- END LOGS ---\n")

    # 4. AI Instruction
    system_instruction = f"""
    You are 'Informatics AI'. 
    DATABASE INFO: {courses_info}
    USER NOTES: {enrolled_notes_context if enrolled_notes_context.strip() else "NONE"}

    STRICT RULE: 
    - If USER NOTES is NOT "NONE", answer using that information.
    - If it is "NONE", ask them to enroll for Rs. 1000.
    """

    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        full_prompt = f"{system_instruction}\n\nUser Question: {user_message}"
        response = model.generate_content(full_prompt)
        bot_reply = response.text if response.text else "Sorry, I couldn't process that."
    except Exception as e:
        print(f"Gemini Error: {e}")
        bot_reply = "Technical error occurred."

    return Response({'response': bot_reply})