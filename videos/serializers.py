# videos/serializers.py
from rest_framework import serializers
from .models import Video
from notes.serializers import NoteSerializer

class VideoSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = ['id', 'course', 'title', 'video_file', 'video_url', 'created_at', 'notes', 'linked_quiz']

    def validate(self, data):
        # ✅ FIX: PATCH ma sirf linked_quiz aauxa, video_file/url hudaina
        # instance bata existing value herna parcha
        instance = getattr(self, 'instance', None)

        file = data.get('video_file', getattr(instance, 'video_file', None))
        url = data.get('video_url', getattr(instance, 'video_url', None))

        if not file and not url:
            raise serializers.ValidationError("Please provide either a video file or a video link.")

        return data