from django.contrib import admin
from .models import Quiz, Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4 # एउटा प्रश्नमा डिफाल्ट ४ वटा अप्सन देखिने

class QuestionInline(admin.TabularInline):
    model = Question
    inlines = [ChoiceInline]
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'created_at']
    inlines = [QuestionInline] # यसले गर्दा क्विज भित्रै Questions थप्न मिल्छ