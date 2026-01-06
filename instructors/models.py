from django.db import models

class Instructor(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='instructors/', blank=True, null=True)

    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
