# videos/serializers.py
from rest_framework import serializers
from .models import Video
from notes.serializers import NoteSerializer  # 👈 Note को Serializer तानिएको

class VideoSerializer(serializers.ModelSerializer):
    # 👈 यो भिडियोसँग जोडिएका सबै नोटहरु सँगै पठाउन
    notes = NoteSerializer(many=True, read_only=True) 

    class Meta:
        model = Video
        # 👈 fields मा 'notes' थपिएको छ
        fields = ['id', 'course', 'title', 'video_file', 'video_url', 'created_at', 'notes'] 

    def validate(self, data):
        file = data.get('video_file')
        url = data.get('video_url')

        if not file and not url:
            raise serializers.ValidationError("Please provide either a video file or a video link.")
        
        return data