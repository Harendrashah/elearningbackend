# instructors/models.py
from django.db import models
from django.contrib.auth.models import User  # ✅ User import garne

class Instructor(models.Model):
    # ✅ User sanga link garne (Euta User ko Euta matra Instructor profile hunxa)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    
    # Baki fields same...
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='instructors/', blank=True, null=True)

    # Social Media
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name