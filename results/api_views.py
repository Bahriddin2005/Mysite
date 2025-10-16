from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Q
import csv
from .models import TestResult, Certificate, UserProgress
from .serializers import TestResultSerializer, CertificateSerializer, UserProgressSerializer


class TestResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return TestResult.objects.all()
        elif user.role == 'teacher':
            return TestResult.objects.filter(attempt__test__created_by=user)
        else:  # student
            return TestResult.objects.filter(attempt__student=user)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        queryset = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="test_results.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Test', 'O\'quvchi', 'Ball', 'Foiz', 'Baho', 'Holati', 'Sana'])
        
        for result in queryset:
            writer.writerow([
                result.attempt.test.title,
                result.attempt.student.get_full_name(),
                result.total_score,
                f"{result.percentage:.1f}%",
                result.grade,
                'O\'tdi' if result.is_passed else 'O\'tmadi',
                result.completed_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Certificate.objects.all()
        elif user.role == 'teacher':
            return Certificate.objects.filter(test__created_by=user)
        else:  # student
            return Certificate.objects.filter(student=user)
    
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        certificate = self.get_object()
        if certificate.is_valid:
            return Response({
                'valid': True,
                'certificate_id': certificate.certificate_id,
                'student': certificate.student.get_full_name(),
                'test': certificate.test.title,
                'score': certificate.score,
                'issued_at': certificate.issued_at
            })
        else:
            return Response({'valid': False}, status=status.HTTP_404_NOT_FOUND)


class UserProgressViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return UserProgress.objects.all()
        elif user.role == 'teacher':
            # O'qituvchilar faqat o'z testlarini topshirgan o'quvchilarni ko'radi
            return UserProgress.objects.filter(
                user__testresult__attempt__test__created_by=user
            ).distinct()
        else:  # student
            return UserProgress.objects.filter(user=user)
