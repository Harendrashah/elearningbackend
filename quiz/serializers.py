from rest_framework import serializers
from .models import Quiz, Question, Choice
from .models import QuizSubmission


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']
        
        # 'write_only': True गर्दा यो फ्रन्टइन्डबाट POST गर्दा सेभ हुन्छ, 
        # तर GET गर्दा (विद्यार्थीलाई देखाउँदा) जाँदैन। चिटिङ प्रुफ! 😎
        extra_kwargs = {
            'is_correct': {'write_only': True}
        }

class QuestionSerializer(serializers.ModelSerializer):
    # read_only=True हटाइयो ताकि एडमिनले पठाएको डेटा सेभ होस्
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']

class QuizSerializer(serializers.ModelSerializer):
    # read_only=True हटाइयो
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        # यदि तपाईंको Quiz मोडलमा course पनि छ भने 'course' थप्नुहोला। 
        # फ्रन्टइन्डले course पनि पठाइरहेको छ।
        fields = ['id', 'title', 'course', 'questions'] 

    def create(self, validated_data):
        # 1. Questions को डेटा झिक्ने
        questions_data = validated_data.pop('questions')
        
        # 2. Quiz बनाउने
        quiz = Quiz.objects.create(**validated_data)
        
        # 3. Questions र Choices बनाउने
        for q_data in questions_data:
            choices_data = q_data.pop('choices')
            question = Question.objects.create(quiz=quiz, **q_data)
            
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
                
        return quiz

class QuizSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = QuizSubmission
        fields = ['id', 'student_name', 'quiz', 'score', 'submitted_at']