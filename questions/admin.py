from django.contrib import admin
from django.utils.html import format_html
from .models import Question, Choice, QuestionAnswer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ('text', 'is_correct', 'order')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'test', 'question_type', 'points', 'order', 'created_at')
    list_filter = ('question_type', 'test__category', 'created_at')
    search_fields = ('text', 'test__title')
    inlines = [ChoiceInline]
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('test', 'question_type', 'text', 'image')
        }),
        ('Sozlamalar', {
            'fields': ('points', 'order', 'explanation', 'correct_answer')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Savol matni'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(test__created_by=request.user)
        return qs


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text_preview', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__question_type')
    search_fields = ('text', 'question__text')
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Variant matni'


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'points_awarded', 'manually_graded', 'first_answered_at')
    list_filter = ('is_correct', 'manually_graded', 'first_answered_at')
    search_fields = ('attempt__user__username', 'question__text')
    readonly_fields = ('first_answered_at', 'last_modified_at')
    
    fieldsets = (
        ('Javob maʼlumotlari', {
            'fields': ('attempt', 'question')
        }),
        ('Javob mazmuni', {
            'fields': ('selected_choices', 'text_answer', 'numeric_answer', 'matching_pairs')
        }),
        ('Baholash', {
            'fields': ('is_correct', 'points_awarded', 'manually_graded', 'grader_feedback', 'graded_by', 'graded_at')
        }),
        ('Statistika', {
            'fields': ('time_spent', 'answer_changed_count'),
            'classes': ('collapse',)
        }),
        ('Vaqt maʼlumotlari', {
            'fields': ('first_answered_at', 'last_modified_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(attempt__test__created_by=request.user)
        return qs
