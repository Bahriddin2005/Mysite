from rest_framework import serializers
from .models import TestResult, Certificate, UserProgress


class TestResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='attempt.student.get_full_name', read_only=True)
    test_title = serializers.CharField(source='attempt.test.title', read_only=True)
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'attempt', 'student_name', 'test_title',
            'total_score', 'percentage', 'grade', 'is_passed',
            'detailed_results', 'feedback', 'completed_at'
        ]
        read_only_fields = ['completed_at']


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    test_title = serializers.CharField(source='test.title', read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'student', 'student_name', 'test', 'test_title',
            'certificate_id', 'score', 'percentage', 'grade',
            'issued_at', 'is_valid', 'verification_url'
        ]
        read_only_fields = ['certificate_id', 'issued_at']


class UserProgressSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'username', 'full_name',
            'total_tests_taken', 'total_tests_passed', 'average_score',
            'total_time_spent', 'achievements', 'last_activity'
        ]
        read_only_fields = ['last_activity', 'updated_at']
