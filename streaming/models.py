from django.db import models
from django.conf import settings
from courses.models import Course

class LiveSession(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='live_sessions'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    zoom_link = models.URLField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"
