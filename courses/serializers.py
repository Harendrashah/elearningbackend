from rest_framework import serializers
from .models import Course, Enrollment
from instructors.models import Instructor
from instructors.serializers import InstructorSerializer

# --- COURSE SERIALIZER ---
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

# --- ENROLLMENT SERIALIZER ---
class EnrollmentSerializer(serializers.ModelSerializer):
    # Table ma Name dekhauna ko lagi
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'student_name', 'student_email', 'course_title', 'enrolled_at']
        
        read_only_fields = ['enrolled_at']

        # ✅ MAIN FIX: Make 'student' optional during validation
        # Yesle garda frontend bata student ID napathauda pani error aaudaina
        extra_kwargs = {
            'student': {'required': False}
        }