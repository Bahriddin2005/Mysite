from rest_framework import serializers
from .models import Question, Choice, QuestionAnswer


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Choice model"""
    
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""
    choices = ChoiceSerializer(many=True, read_only=True)
    test_title = serializers.CharField(source='test.title', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'test', 'test_title', 'question_type', 'text', 'image',
                 'points', 'order', 'explanation', 'correct_answer', 'choices',
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class QuestionDetailSerializer(QuestionSerializer):
    """Detailed serializer for Question model"""
    
    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ['explanation']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating questions"""
    choices = ChoiceSerializer(many=True, required=False)
    
    class Meta:
        model = Question
        fields = ['test', 'question_type', 'text', 'image', 'points', 
                 'order', 'explanation', 'correct_answer', 'choices']
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        
        return question


class QuestionAnswerSerializer(serializers.ModelSerializer):
    """Serializer for QuestionAnswer model"""
    question_text = serializers.CharField(source='question.text', read_only=True)
    student_name = serializers.CharField(source='attempt.student.get_full_name', read_only=True)
    
    class Meta:
        model = QuestionAnswer
        fields = ['id', 'attempt', 'question', 'question_text', 'student_name',
                 'answer', 'is_correct', 'points_earned', 'answered_at']
        read_only_fields = ['is_correct', 'points_earned', 'answered_at']


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting answers"""
    question_id = serializers.IntegerField()
    answer = serializers.JSONField()
    
    def validate_question_id(self, value):
        try:
            question = Question.objects.get(id=value)
            return question
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question not found.")
