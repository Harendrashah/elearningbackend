from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import google.generativeai as genai

# --- IMPORTS (तपाईंको मोडेलको नाम चेक गर्नुहोला) ---
from courses.models import Course 
# ⚠️ तलका नामहरू चेक गर्नुहोस: तपाईको models.py मा class को नाम जे छ त्यही राख्नुहोस
# उदाहरण: from streaming.models import Stream (यदि क्लासको नाम Stream छ भने)
try:
    from streaming.models import Stream  # वा LiveSession?
    from videos.models import Video      # वा Lesson?
except ImportError:
    pass # यदि मोडेल भेटिएन भने एरर नआओस् भनेर

# तपाईंको API KEY
API_KEY = "AIzaSyCGj1dpjKQIlCdZsTbg7OnNniO6MU3VDFo"

genai.configure(api_key=API_KEY)

@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_api(request):
    user_message = request.data.get('message', '')

    # ================= 1. DATABASE DATA FETCHING =================

    # --- A. COURSES & TEACHERS ---
    courses_info = "COURSES AVAILABLE:\n"
    try:
        all_courses = Course.objects.all()
        if not all_courses:
             courses_info += "No courses found.\n"
        else:
            for course in all_courses:
                # Teacher को नाम तान्ने (यदि instructor फिल्ड छ भने)
                # यदि तपाईको मोडलमा 'teacher' वा 'author' छ भने त्यही अनुसार फेर्नुहोस
                try:
                    teacher_name = course.instructor.username if course.instructor else "Unknown Teacher"
                except AttributeError:
                    teacher_name = "Instructor Info Not Available"

                courses_info += f"- Course: {course.title}, Price: Rs. {course.price}, Teacher: {teacher_name}\n"
    except Exception as e:
        courses_info += "Course data unavailable.\n"

    # --- B. LIVE CLASSES (STREAMING) ---
    live_class_info = "\nUPCOMING LIVE CLASSES:\n"
    try:
        # यहाँ Stream.objects.all() प्रयोग गरिएको छ
        all_streams = Stream.objects.all() 
        if not all_streams:
            live_class_info += "No live classes scheduled currently.\n"
        else:
            for stream in all_streams:
                # title र time तपाईको मोडल अनुसार फेर्नुहोस
                live_class_info += f"- Topic: {stream.title}, Scheduled At: {stream.created_at}\n" 
    except Exception:
        live_class_info += "Live class info unavailable (Check models).\n"

    # --- C. VIDEO RESOURCES ---
    video_info = "\nVIDEO LIBRARY:\n"
    try:
        all_videos = Video.objects.all()
        if not all_videos:
            video_info += "No videos uploaded yet.\n"
        else:
            for video in all_videos:
                video_info += f"- Video Title: {video.title}\n"
    except Exception:
        video_info += "Video info unavailable.\n"


    # ================= 2. SYSTEM INSTRUCTION =================
    
    system_instruction = f"""
    You are a helpful AI assistant for 'Smart Learning Platform'.
    
    # --- REAL-TIME DATABASE INFORMATION ---
    {courses_info}
    {live_class_info}
    {video_info}

    # --- ORGANIZATION CONTACT ---
    OFFICE LOCATION: Putalisadak, Kathmandu, Nepal
    PHONE: 9801234567
    EMAIL: info@smartlearning.com

    # --- INSTRUCTIONS ---
    1. Answer strictly based on the DATABASE INFORMATION provided above.
    2. If asked about Teachers, use the Course info.
    3. If asked about Live Classes or Videos, use the respective sections.
    4. LANGUAGE:
       - User speaks Nepali -> Reply in Nepali.
       - User speaks English -> Reply in English.
    """
    
    # ================= 3. AI RESPONSE =================
    try:
        if not API_KEY:
            return Response({'response': "API Key Missing"})

        model = genai.GenerativeModel('gemini-flash-latest')
        
        full_prompt = f"{system_instruction}\n\nUser Question: {user_message}"
        
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            bot_reply = response.text
        else:
            bot_reply = "Sorry, no response generated."

    except Exception as e:
        print(f"Gemini Error: {e}")
        if "429" in str(e):
             bot_reply = "System is busy (Quota Exceeded). Please try again later."
        elif "404" in str(e):
             bot_reply = "Model configuration error."
        else:
             bot_reply = "System Error. Please try again."

    return Response({'response': bot_reply})