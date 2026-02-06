from rest_framework import viewsets, parsers
from .models import Video
from .serializers import VideoSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer
    
    # IMPORTANT: Frontend ले 'FormData' पठाउँदा यी दुई parser चाहिन्छ
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    # (Optional) यदि लगइन गरेको Admin ले मात्र हाल्न पाउने बनाउने हो भने:
    # permission_classes = [permissions.IsAdminUser]