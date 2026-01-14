from rest_framework import serializers
from .models import LiveSession

class LiveSessionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = LiveSession
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']
