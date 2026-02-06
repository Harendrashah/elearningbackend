from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'course', 'title', 'video_file', 'video_url', 'created_at']

    # Validation: File वा Link मध्ये एउटा अनिवार्य हुनुपर्छ
    def validate(self, data):
        file = data.get('video_file')
        url = data.get('video_url')

        if not file and not url:
            raise serializers.ValidationError("Please provide either a video file or a video link.")
        
        return data