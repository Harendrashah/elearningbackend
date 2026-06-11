# quiz/serializers.py
from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizSubmission


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']
        # ✅ write_only HATAYO — yo nai 500 error ko karan thiyo


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    linked_video_title = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course',
            'questions', 'created_at',
            'linked_video_title',
        ]
        read_only_fields = ['created_at']

    def get_linked_video_title(self, obj):
        video = obj.linked_videos.first()
        return video.title if video else None

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        for q_data in questions_data:
            choices_data = q_data.pop('choices')
            question = Question.objects.create(quiz=quiz, **q_data)
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        if questions_data is not None:
            instance.questions.all().delete()
            for q_data in questions_data:
                choices_data = q_data.pop('choices')
                question = Question.objects.create(quiz=instance, **q_data)
                for choice_data in choices_data:
                    Choice.objects.create(question=question, **choice_data)
        return instance


# ✅ QuizAdminSerializer — views.py le import garxa
class QuizAdminSerializer(QuizSerializer):
    pass


class QuizSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizSubmission
        fields = ['id', 'student_name', 'quiz', 'quiz_title', 'score', 'submitted_at']