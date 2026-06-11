from django.db import models

class Video(models.Model):
    # 👇 यहाँ हेर्नुस्, मैले 'courses.Course' बनाएको छु
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='videos')
    
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='course_videos/', null=True, blank=True)
    video_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    linked_quiz = models.ForeignKey(
        'quiz.Quiz',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_videos'
    )   

    def __str__(self):
        return self.title