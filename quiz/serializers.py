# quiz/serializers.py
from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizSubmission


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']
        extra_kwargs = {
            # ✅ Student le GET garda is_correct dekhinna (anti-cheat)
            'is_correct': {'write_only': True}
        }


# ✅ Admin/Teacher ko lagi — is_correct dekhcha
class ChoiceAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        # ✅ description add gareko
        fields = ['id', 'title', 'description', 'course', 'questions', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)

        for q_data in questions_data:
            choices_data = q_data.pop('choices')
            question = Question.objects.create(quiz=quiz, **q_data)
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)

        return quiz

    # ✅ Update pani add gareko
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        if questions_data is not None:
            # Purana questions delete garne, naya banauне
            instance.questions.all().delete()
            for q_data in questions_data:
                choices_data = q_data.pop('choices')
                question = Question.objects.create(quiz=instance, **q_data)
                for choice_data in choices_data:
                    Choice.objects.create(question=question, **choice_data)

        return instance


class QuizSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizSubmission
        fields = ['id', 'student_name', 'quiz', 'quiz_title', 'score', 'submitted_at']