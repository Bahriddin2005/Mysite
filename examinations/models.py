from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Category(models.Model):
    """
    Test categories (Math, Physics, Chemistry, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'examinations_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']


class Test(models.Model):
    """
    Main Test model
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    TYPE_CHOICES = (
        ('one_time', 'One Time'),
        ('repeatable', 'Repeatable'),
        ('practice', 'Practice Mode'),
    )
    
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    # Basic information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tests')
    
    # Test configuration
    test_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='one_time')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    grade_level = models.CharField(max_length=20, blank=True, help_text="Target grade level")
    
    # Timing and scoring
    time_limit = models.PositiveIntegerField(help_text="Time limit in minutes", validators=[MinValueValidator(1)])
    max_score = models.PositiveIntegerField(default=100)
    pass_mark = models.PositiveIntegerField(help_text="Minimum score to pass")
    
    # Access control
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    max_attempts = models.PositiveIntegerField(default=1, help_text="Maximum attempts per user")
    
    # Content settings
    show_results_immediately = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=True)
    randomize_choices = models.BooleanField(default=True)
    
    # Anti-cheating settings
    monitor_browser_focus = models.BooleanField(default=True)
    disable_copy_paste = models.BooleanField(default=True)
    full_screen_mode = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics (denormalized for performance)
    total_attempts = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    pass_rate = models.FloatField(default=0.0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('test_detail', kwargs={'slug': self.slug})
    
    @property
    def total_questions(self):
        return self.questions.count()
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def duration_display(self):
        hours = self.time_limit // 60
        minutes = self.time_limit % 60
        if hours:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'examinations_test'
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
        ordering = ['-created_at']


class TestAttempt(models.Model):
    """
    User's attempt at taking a test
    """
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('timeout', 'Timed Out'),
    )
    
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_attempts')
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    time_spent = models.PositiveIntegerField(default=0, help_text="Time spent in seconds")
    
    # Scoring
    total_score = models.FloatField(default=0.0)
    percentage_score = models.FloatField(default=0.0)
    max_possible_score = models.PositiveIntegerField(default=0)
    
    # Status and results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    is_passed = models.BooleanField(default=False)
    
    # Security and monitoring
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    focus_lost_count = models.PositiveIntegerField(default=0)
    suspicious_activity = models.JSONField(default=dict, blank=True)
    
    # Auto-save data
    current_question_index = models.PositiveIntegerField(default=0)
    answers_data = models.JSONField(default=dict, blank=True)
    
    # Grading
    auto_graded_at = models.DateTimeField(blank=True, null=True)
    manually_graded_at = models.DateTimeField(blank=True, null=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='graded_attempts')
    
    # Feedback
    instructor_feedback = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if self.finished_at and not self.time_spent:
            self.time_spent = int((self.finished_at - self.started_at).total_seconds())
        super().save(*args, **kwargs)
    
    @property
    def duration_display(self):
        hours = self.time_spent // 3600
        minutes = (self.time_spent % 3600) // 60
        seconds = self.time_spent % 60
        
        if hours:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    
    @property
    def is_active(self):
        return self.status == 'in_progress'
    
    def __str__(self):
        return f"{self.user.username} - {self.test.title}"
    
    class Meta:
        db_table = 'examinations_testattempt'
        verbose_name = 'Test Attempt'
        verbose_name_plural = 'Test Attempts'
        ordering = ['-started_at']
        unique_together = ['test', 'user', 'started_at']


class TestSession(models.Model):
    """
    Real-time test session data for auto-save and monitoring
    """
    attempt = models.OneToOneField(TestAttempt, on_delete=models.CASCADE, related_name='session')
    session_key = models.CharField(max_length=40)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Real-time tracking
    current_question = models.PositiveIntegerField(default=0)
    time_remaining = models.PositiveIntegerField(default=0)  # seconds
    answers_buffer = models.JSONField(default=dict)  # temporary answers before saving
    
    # Browser monitoring
    window_focus = models.BooleanField(default=True)
    full_screen = models.BooleanField(default=True)
    last_heartbeat = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session: {self.attempt}"
    
    class Meta:
        db_table = 'examinations_testsession'
        verbose_name = 'Test Session'
        verbose_name_plural = 'Test Sessions'
