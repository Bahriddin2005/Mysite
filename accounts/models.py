from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with additional fields for test system
    """
    USER_ROLES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    school_class = models.CharField(max_length=10, blank=True, null=True, help_text="Student's class (e.g., 9-A, 10-B)")
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    is_active_student = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Additional fields for analytics
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class UserProfile(models.Model):
    """
    Extended profile information for users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    
    # Academic information
    grade_level = models.CharField(max_length=20, blank=True, help_text="Academic level")
    subjects_of_interest = models.JSONField(default=list, blank=True)
    
    # Preferences
    language_preference = models.CharField(max_length=10, default='uz', choices=[
        ('uz', 'Uzbek'),
        ('ru', 'Russian'),
        ('en', 'English'),
    ])
    timezone = models.CharField(max_length=50, default='Asia/Tashkent')
    
    # Privacy settings
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    allow_messages = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    class Meta:
        db_table = 'accounts_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
