# notes/models.py
from django.db import models
from courses.models import Course
from videos.models import Video  # 👈 Video मोडल तानिएको

# notes/models.py मा यो लाइन थप्नुहोस्
class Note(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='notes', null=True, blank=True) 
    file = models.FileField(upload_to='notes/')
    
    # 👈 यो लाइन नयाँ थप्नुहोस्: यसले नै AI लाई डेटा दिन्छ
    content = models.TextField(null=True, blank=True, help_text="AI ले पढ्नको लागि यहाँ नोटको टेक्स्ट पेस्ट गर्नुहोस्")
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title