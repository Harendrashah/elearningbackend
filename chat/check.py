# check_models.py
import google.generativeai as genai

API_KEY = "AIzaSyCGj1dpjKQIlCdZsTbg7OnNniO6MU3VDFo"  # तपाईंको API Key
genai.configure(api_key=API_KEY)

print("Available Models for you:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")