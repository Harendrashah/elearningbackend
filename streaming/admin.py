from django.contrib import admin
from .models import LiveSession

@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'end_time')
