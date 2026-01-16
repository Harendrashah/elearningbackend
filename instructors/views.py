# instructors/views.py
from rest_framework import viewsets, permissions
from .models import Instructor
from .serializers import InstructorSerializer

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer

    def get_permissions(self):
        # 1. List/Retrieve (Herna): Sabai le pauchan
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        
        # 2. Create/Update/Delete: Only Admin (Security ko lagi)
        return [permissions.IsAdminUser()]