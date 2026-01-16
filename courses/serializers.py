# courses/serializers.py
from rest_framework import serializers
from .models import Course, Enrollment
from instructors.models import Instructor
from instructors.serializers import InstructorSerializer

class CourseSerializer(serializers.ModelSerializer):
    # GET garda: Pura details aauxa (Nested Object)
    instructor = InstructorSerializer(read_only=True)
    
    # POST/PUT garda: ID pathaunu parcha
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=Instructor.objects.all(), 
        source='instructor',
        write_only=True,
        required=False  # Admin le select garena vane login user nai bascha
    )

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['created_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    # ✅ Table ma Name dekhauna ko lagi (Fixes "Unknown" issue)
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'student_name', 'student_email', 'course_title', 'enrolled_at']
        
        # ⚠️ MISTAKE WAS HERE: 'student' lai read_only ma narakhnuhos!
        read_only_fields = ['enrolled_at']