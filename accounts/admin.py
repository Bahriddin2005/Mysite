from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'full_name', 'is_active_student', 'school_class', 'created_at')
    list_filter = ('role', 'is_active', 'is_active_student', 'school_class', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'student_id')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('role', 'phone_number', 'birth_date', 'school_class', 
                      'student_id', 'is_active_student', 'profile_image')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_activity')
    actions = ['approve_users', 'block_users', 'export_users']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')
    
    def full_name(self, obj):
        return obj.full_name or 'Nomi kiritilmagan'
    full_name.short_description = 'Ism familiya'
    
    def approve_users(self, request, queryset):
        queryset.update(is_active=True, is_active_student=True)
        self.message_user(request, f"{queryset.count()} foydalanuvchi tasdiqlandi.")
    approve_users.short_description = "Foydalanuvchilarni tasdiqlash"
    
    def block_users(self, request, queryset):
        queryset.update(is_active=False, is_active_student=False)
        self.message_user(request, f"{queryset.count()} foydalanuvchi bloklandi.")
    block_users.short_description = "Foydalanuvchilarni bloklash"
    
    def export_users(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'Role', 'Full Name', 'Active', 'Created'])
        
        for user in queryset:
            writer.writerow([
                user.username,
                user.email,
                user.get_role_display(),
                user.get_full_name(),
                'Ha' if user.is_active else 'Yo\'q',
                user.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    export_users.short_description = "Foydalanuvchilarni eksport qilish"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'language_preference', 'grade_level', 'show_contact_info', 'created_at')
    list_filter = ('language_preference', 'grade_level', 'show_email', 'show_phone')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('bio', 'location', 'website', 'grade_level', 'subjects_of_interest')
        }),
        ('Sozlamalar', {
            'fields': ('language_preference', 'timezone')
        }),
        ('Maxfiylik sozlamalari', {
            'fields': ('show_email', 'show_phone', 'allow_messages')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def show_contact_info(self, obj):
        if obj.show_email and obj.show_phone:
            return format_html('<span style="color: green;">✓ Hammasi</span>')
        elif obj.show_email:
            return format_html('<span style="color: orange;">✓ Faqat email</span>')
        elif obj.show_phone:
            return format_html('<span style="color: orange;">✓ Faqat telefon</span>')
        else:
            return format_html('<span style="color: red;">✗ Yashirin</span>')
    show_contact_info.short_description = 'Aloqa ma\'lumotlari'
