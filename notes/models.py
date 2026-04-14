import docx  # यो माथि थप्नुहोस्
from django.db import models
from courses.models import Course
from videos.models import Video

class Note(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='notes', null=True, blank=True) 
    file = models.FileField(upload_to='notes/')
    content = models.TextField(null=True, blank=True, help_text="AI ले पढ्नको लागि यहाँ नोटको टेक्स्ट पेस्ट गर्नुहोस्")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # यो नयाँ 'save' मेथड थप्नुहोस् जसले गर्दा फाइलबाट टेक्स्ट आफैं तानिन्छ
    def save(self, *args, **kwargs):
        if self.file and self.file.name.endswith('.docx') and not self.content:
            try:
                doc = docx.Document(self.file)
                full_text = [para.text for para in doc.paragraphs]
                self.content = "\n".join(full_text)
            except Exception as e:
                print(f"Error reading docx: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title