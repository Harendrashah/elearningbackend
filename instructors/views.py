from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Instructor
from .serializers import InstructorSerializer

class InstructorListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        instructors = Instructor.objects.all()
        serializer = InstructorSerializer(instructors, many=True)
        return Response(serializer.data)
