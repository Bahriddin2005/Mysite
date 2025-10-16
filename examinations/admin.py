from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
import csv
from .models import Category, Test, TestAttempt, TestSession


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'test_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'name': ('name',)}
    
    def test_count(self, obj):
        return obj.tests.count()
    test_count.short_description = 'Testlar soni'


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'difficulty', 'status', 'question_count', 'attempt_count', 'created_at')
    list_filter = ('category', 'difficulty', 'status', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'description', 'category', 'created_by')
        }),
        ('Test sozlamalari', {
            'fields': ('difficulty', 'duration_minutes', 'total_points', 'passing_score', 'attempts_allowed')
        }),
        ('Qo\'shimcha sozlamalar', {
            'fields': ('randomize_questions', 'show_results_immediately', 'allow_review', 'is_published', 'is_proctored'),
            'classes': ('collapse',)
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_tests', 'unpublish_tests', 'export_test_results']
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Savollar soni'
    
    def attempt_count(self, obj):
        return obj.attempts.count()
    attempt_count.short_description = 'Urinishlar soni'
    
    def publish_tests(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, f"{queryset.count()} test nashr qilindi.")
    publish_tests.short_description = "Tanlangan testlarni nashr qilish"
    
    def unpublish_tests(self, request, queryset):
        queryset.update(status='draft')
        self.message_user(request, f"{queryset.count()} test nashrdan olib tashlandi.")
    unpublish_tests.short_description = "Tanlangan testlarni nashrdan olib tashlash"
    
    def export_test_results(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="test_results.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Test nomi', 'O\'quvchi', 'Ball', 'Foiz', 'Holati', 'Sana'])
        
        for test in queryset:
            for attempt in test.attempts.all():
                writer.writerow([
                    test.title,
                    attempt.student.get_full_name(),
                    attempt.score or 0,
                    f"{attempt.percentage or 0:.1f}%",
                    'O\'tdi' if attempt.is_passed else 'O\'tmadi',
                    attempt.started_at.strftime('%Y-%m-%d %H:%M')
                ])
        
        return response
    export_test_results.short_description = "Test natijalarini eksport qilish"


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('test', 'user', 'total_score', 'percentage_score', 'is_passed', 'status', 'started_at')
    list_filter = ('is_passed', 'status', 'started_at')
    search_fields = ('test__title', 'user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('started_at', 'finished_at', 'time_spent', 'auto_graded_at', 'manually_graded_at')
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Test ma\'lumotlari', {
            'fields': ('test', 'student')
        }),
        ('Natijalar', {
            'fields': ('score', 'percentage', 'is_passed', 'is_completed')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('started_at', 'completed_at', 'duration_seconds')
        }),
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('answers_data', 'browser_info', 'ip_address', 'focus_lost_count', 'tab_switch_count'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_attempts']
    
    def duration_display(self, obj):
        if obj.duration_seconds:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return "-"
    duration_display.short_description = 'Davomiyligi'
    
    def export_attempts(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="test_attempts.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Test', 'O\'quvchi', 'Email', 'Ball', 'Foiz', 'Holati', 
            'Boshlangan vaqt', 'Tugagan vaqt', 'Davomiyligi', 'IP manzil'
        ])
        
        for attempt in queryset:
            writer.writerow([
                attempt.test.title,
                attempt.student.get_full_name(),
                attempt.student.email,
                attempt.score or 0,
                f"{attempt.percentage or 0:.1f}%",
                'O\'tdi' if attempt.is_passed else 'O\'tmadi',
                attempt.started_at.strftime('%Y-%m-%d %H:%M'),
                attempt.completed_at.strftime('%Y-%m-%d %H:%M') if attempt.completed_at else '-',
                self.duration_display(attempt),
                attempt.ip_address or '-'
            ])
        
        return response
    export_attempts.short_description = "Urinishlarni eksport qilish"


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'current_question', 'time_remaining', 'last_activity', 'is_active')
    list_filter = ('is_active', 'last_activity')
    search_fields = ('attempt__test__title', 'attempt__user__username')
    readonly_fields = ('last_activity',)
