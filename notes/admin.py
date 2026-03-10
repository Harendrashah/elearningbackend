# notes/admin.py
from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    # 👈 'video' थपिएको छ
    list_display = ('title', 'course', 'video', 'uploaded_at')
    list_filter = ('course', 'video')
    search_fields = ('title',)