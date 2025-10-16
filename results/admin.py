from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import TestResult, Certificate, UserProgress


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'points_earned', 'percentage_score', 'grade_letter', 'is_passed', 'created_at')
    list_filter = ('is_passed', 'grade_letter', 'created_at')
    search_fields = ('attempt__user__username', 'attempt__test__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Test maʼlumotlari', {
            'fields': ('attempt',)
        }),
        ('Natijalar', {
            'fields': ('points_earned', 'percentage_score', 'grade_letter', 'is_passed')
        }),
        ('Batafsil natijalar', {
            'fields': ('total_questions', 'correct_answers', 'incorrect_answers', 'unanswered_questions'),
            'classes': ('collapse',)
        }),
        ('Vaqt maʼlumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_results']
    
    def export_results(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="detailed_results.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Test', 'O\'quvchi', 'Email', 'Jami ball', 'Foiz', 'Baho', 
            'Holati', 'Tugagan vaqt'
        ])
        
        for result in queryset:
            writer.writerow([
                result.attempt.test.title,
                result.attempt.student.get_full_name(),
                result.attempt.student.email,
                result.total_score,
                f"{result.percentage:.1f}%",
                result.grade,
                'O\'tdi' if result.is_passed else 'O\'tmadi',
                result.completed_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_results.short_description = "Natijalarni eksport qilish"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('result', 'certificate_number', 'recipient_name', 'score_achieved', 'issued_at', 'is_verified')
    list_filter = ('is_verified', 'issued_at', 'template_used')
    search_fields = ('recipient_name', 'test_title', 'certificate_number')
    readonly_fields = ('certificate_number', 'verification_code', 'issued_at')
    
    fieldsets = (
        ('Sertifikat maʼlumotlari', {
            'fields': ('result', 'certificate_number', 'verification_code')
        }),
        ('Natija maʼlumotlari', {
            'fields': ('recipient_name', 'test_title', 'completion_date', 'score_achieved')
        }),
        ('Qoʻshimcha maʼlumotlar', {
            'fields': ('is_verified', 'issued_at', 'issued_by', 'certificate_pdf'),
        }),
    )
    
    actions = ['revoke_certificates', 'export_certificates']
    
    def revoke_certificates(self, request, queryset):
        queryset.update(is_valid=False)
        self.message_user(request, f"{queryset.count()} sertifikat bekor qilindi.")
    revoke_certificates.short_description = "Sertifikatlarni bekor qilish"
    
    def export_certificates(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="certificates.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Sertifikat ID', 'O\'quvchi', 'Test', 'Ball', 'Foiz', 
            'Baho', 'Berilgan sana', 'Holati'
        ])
        
        for cert in queryset:
            writer.writerow([
                cert.certificate_id,
                cert.student.get_full_name(),
                cert.test.title,
                cert.score,
                f"{cert.percentage:.1f}%",
                cert.grade,
                cert.issued_at.strftime('%Y-%m-%d'),
                'Faol' if cert.is_valid else 'Bekor qilingan'
            ])
        
        return response
    export_certificates.short_description = "Sertifikatlarni eksport qilish"


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'tests_taken', 'tests_passed', 'average_score', 'last_activity_date')
    list_filter = ('skill_level', 'category', 'last_activity_date', 'user__role')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user', 'category')
        }),
        ('Statistikalar', {
            'fields': ('tests_taken', 'tests_passed', 'average_score', 'best_score', 'latest_score')
        }),
        ('Malaka darajasi', {
            'fields': ('skill_level', 'mastery_percentage', 'achievements', 'badges_earned')
        }),
        ('Qoʻshimcha maʼlumotlar', {
            'fields': ('total_study_time', 'streak_count', 'first_attempt_date', 'last_activity_date'),
            'classes': ('collapse',)
        }),
    )
