# instructors/admin.py
from django.contrib import admin
from .models import Instructor

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'user') # ✅ User pani list ma dekhine vayo
    search_fields = ('name', 'subject')