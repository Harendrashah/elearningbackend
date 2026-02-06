from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    # Admin Table मा के-के देखाउने?
    list_display = ('id', 'title', 'course', 'get_video_type', 'created_at')
    
    # कुन कुराबाट फिल्टर गर्ने? (Filter by Course)
    list_filter = ('course',)
    
    # के सर्च गर्न मिल्ने? (Search by Title or Course Name)
    search_fields = ('title', 'course__title')

    # भिडियो Link छ कि File छ भनेर देखाउने कस्टम लोजिक
    def get_video_type(self, obj):
        if obj.video_file:
            return "📁 File Uploaded"
        elif obj.video_url:
            return "🔗 Link Provided"
        else:
            return "❌ No Video"
    
    get_video_type.short_description = 'Video Source'