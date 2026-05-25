# quiz/admin.py
from django.contrib import admin
from .models import Quiz, Question, Choice, QuizSubmission


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['text', 'quiz']
    list_filter = ['quiz']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    # ✅ Choice inline hata, alag admin page bata manage garne


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'created_at']
    list_filter = ['course']
    inlines = [QuestionInline]


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'submitted_at']
    list_filter = ['quiz']
    readonly_fields = ['student', 'quiz', 'score', 'submitted_at']