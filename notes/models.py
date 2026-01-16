# notes/models.py
from django.db import models
from courses.models import Course

class Note(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)  # ✅ make sure this exists

    def __str__(self):
        return self.title
