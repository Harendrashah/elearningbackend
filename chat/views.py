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
    user = request.user  # लगइन भएको युजर
    
    courses_info = ""
    enrolled_notes_context = ""

    # ================= 1. DATABASE DATA FETCHING =================

    # --- A. सबै उपलब्ध कोर्षहरूको जानकारी तान्ने ---
    try:
        all_courses = Course.objects.all()
        if not all_courses:
            courses_info = "No courses available at the moment."
        else:
            for course in all_courses:
                courses_info += f"- Course: {course.title}, Price: Rs. {course.price}\n"
    except Exception as e:
        courses_info = "Error fetching courses."

    # --- B. युजर लगइन छ भने उसको Enrollment र Notes चेक गर्ने ---
    if user.is_authenticated:
        try:
            # Enrollment मोडलमा 'student' फिल्ड छ भने (तपाईंको अघिल्लो कोड अनुसार)
            user_enrollments = Enrollment.objects.filter(student=user)
            
            # यदि 'student' ले काम गरेन भने 'user=user' ट्राइ गर्नुहोस्:
            # user_enrollments = Enrollment.objects.filter(user=user)

            if user_enrollments.exists():
                enrolled_notes_context = "\n--- PRIVATE NOTES FOR THIS ENROLLED STUDENT ---\n"
                for enrollment in user_enrollments:
                    # इनरोल भएको कोर्षसँग सम्बन्धित नोटहरू तान्ने
                    course_notes = Note.objects.filter(course=enrollment.course)
                    for note in course_notes:
                        # नोटको 'content' (TextField) खाली छैन भने मात्र एआईलाई दिने
                        if note.content:
                            enrolled_notes_context += f"TOPIC: {note.title}\nCONTENT: {note.content}\n\n"
            
            # टर्मिनलमा डिबग गर्नको लागि (VS Code Terminal मा हेर्नुहोस)
            print(f"DEBUG: User '{user.username}' has {user_enrollments.count()} enrollments.")
            
        except Exception as e:
            print(f"Enrollment Check Error: {e}")

    # ================= 2. SYSTEM INSTRUCTION =================
    
    system_instruction = f"""
    You are 'Informatics AI', a smart academic tutor for 'Informatic Education Path'.
    
    # DATABASE INFORMATION:
    AVAILABLE COURSES:
    {courses_info}

    USER'S PRIVATE NOTES (ONLY IF ENROLLED):
    {enrolled_notes_context if enrolled_notes_context else "NONE (User is either guest or not enrolled in any course)."}

    # STRICT RULES:
    1. If PRIVATE NOTES is NOT "NONE", the user is an ENROLLED student. 
    2. Answer their subject-related questions (like programming or theory) using the provided PRIVATE NOTES content.
    3. Do NOT ask them to enroll if you see the relevant answer in the PRIVATE NOTES section.
    4. If PRIVATE NOTES is "NONE" and they ask for specific programs or theory, tell them: 
       "Please enroll in our course (Rs. 1000) to access private notes and solutions."
    5. LANGUAGE: Reply in Nepali or English based on the user's question style.
    6. Always be helpful and professional.
    """

    # ================= 3. AI RESPONSE GENERATION =================
    try:
        # मोडलको नाम 'gemini-1.5-flash-latest' वा 'gemini-pro' राख्नुहोस्
        model = genai.GenerativeModel('gemini-flash-latest')
        
        full_prompt = f"{system_instruction}\n\nUser Question: {user_message}"
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            bot_reply = response.text
        else:
            bot_reply = "माफ गर्नुहोला, म अहिले जवाफ दिन असमर्थ छु।"

    except Exception as e:
        print(f"Gemini API Error: {e}")
        bot_reply = "सिस्टममा केही प्राविधिक समस्या आयो। कृपया केही समयपछि प्रयास गर्नुहोस्।"

    return Response({'response': bot_reply})