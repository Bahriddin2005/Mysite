from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class TestResult(models.Model):
    """
    Final results and analytics for completed tests
    """
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.OneToOneField('examinations.TestAttempt', on_delete=models.CASCADE, related_name='result')
    
    # Detailed scoring
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)
    unanswered_questions = models.PositiveIntegerField(default=0)
    partial_credit_questions = models.PositiveIntegerField(default=0)
    
    # Score breakdown
    points_earned = models.FloatField(default=0.0)
    points_possible = models.PositiveIntegerField()
    percentage_score = models.FloatField()
    grade_letter = models.CharField(max_length=2, blank=True)  # A, B, C, D, F
    
    # Pass/Fail status
    is_passed = models.BooleanField()
    pass_threshold = models.FloatField()
    
    # Timing analysis
    time_allocated = models.PositiveIntegerField()  # in seconds
    time_used = models.PositiveIntegerField()       # in seconds
    time_efficiency = models.FloatField(default=0.0)  # percentage of time used
    
    # Performance by category/topic
    category_scores = models.JSONField(default=dict)  # {category: {correct: X, total: Y}}
    difficulty_breakdown = models.JSONField(default=dict)  # {easy: X%, medium: Y%, hard: Z%}
    
    # Ranking and percentiles
    percentile_rank = models.FloatField(blank=True, null=True)
    class_rank = models.PositiveIntegerField(blank=True, null=True)
    total_participants = models.PositiveIntegerField(blank=True, null=True)
    
    # Certificate information
    certificate_issued = models.BooleanField(default=False)
    certificate_number = models.CharField(max_length=50, blank=True, unique=True)
    certificate_date = models.DateTimeField(blank=True, null=True)
    
    # Feedback and recommendations
    instructor_feedback = models.TextField(blank=True)
    automated_feedback = models.TextField(blank=True)
    improvement_areas = models.JSONField(default=list)
    recommended_study_topics = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.certificate_number and self.is_passed and not self.certificate_issued:
            self.generate_certificate_number()
        super().save(*args, **kwargs)
    
    def generate_certificate_number(self):
        """Generate unique certificate number"""
        year = timezone.now().year
        test_prefix = self.attempt.test.category.slug.upper()[:3]
        unique_id = str(uuid.uuid4())[:8].upper()
        self.certificate_number = f"CERT-{year}-{test_prefix}-{unique_id}"
    
    def calculate_grade_letter(self):
        """Calculate letter grade based on percentage"""
        if self.percentage_score >= 90:
            return 'A'
        elif self.percentage_score >= 80:
            return 'B'
        elif self.percentage_score >= 70:
            return 'C'
        elif self.percentage_score >= 60:
            return 'D'
        else:
            return 'F'
    
    @property
    def accuracy_rate(self):
        if self.total_questions == 0:
            return 0
        return (self.correct_answers / self.total_questions) * 100
    
    @property
    def completion_rate(self):
        answered = self.total_questions - self.unanswered_questions
        if self.total_questions == 0:
            return 0
        return (answered / self.total_questions) * 100
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.attempt.test.title} - {self.percentage_score:.1f}%"
    
    class Meta:
        db_table = 'results_testresult'
        verbose_name = 'Test Result'
        verbose_name_plural = 'Test Results'
        ordering = ['-created_at']


class Certificate(models.Model):
    """
    Digital certificates for successful test completions
    """
    result = models.OneToOneField(TestResult, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=50, unique=True)
    
    # Certificate content
    recipient_name = models.CharField(max_length=200)
    test_title = models.CharField(max_length=200)
    completion_date = models.DateField()
    score_achieved = models.FloatField()
    
    # Verification
    verification_code = models.CharField(max_length=100, unique=True)
    is_verified = models.BooleanField(default=True)
    
    # File storage
    certificate_pdf = models.FileField(upload_to='certificates/', blank=True, null=True)
    template_used = models.CharField(max_length=100, default='default')
    
    # Metadata
    issued_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_certificates')
    
    # Digital signature (basic)
    signature_hash = models.CharField(max_length=256, blank=True)
    
    def generate_verification_code(self):
        """Generate unique verification code"""
        import hashlib
        data = f"{self.certificate_number}{self.recipient_name}{self.completion_date}"
        return hashlib.sha256(data.encode()).hexdigest()[:20].upper()
    
    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Certificate: {self.certificate_number} - {self.recipient_name}"
    
    class Meta:
        db_table = 'results_certificate'
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-issued_at']


class AnalyticsReport(models.Model):
    """
    Periodic analytics reports for tests and users
    """
    REPORT_TYPES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Range'),
    )
    
    # Report metadata
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Scope
    test = models.ForeignKey('examinations.Test', on_delete=models.CASCADE, blank=True, null=True, related_name='analytics_reports')
    category = models.ForeignKey('examinations.Category', on_delete=models.CASCADE, blank=True, null=True, related_name='analytics_reports')
    user_group = models.CharField(max_length=50, blank=True)  # class, grade level, etc.
    
    # Analytics data
    total_attempts = models.PositiveIntegerField(default=0)
    total_completions = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    median_score = models.FloatField(default=0.0)
    pass_rate = models.FloatField(default=0.0)
    
    # Detailed analytics
    score_distribution = models.JSONField(default=dict)  # {range: count}
    time_analytics = models.JSONField(default=dict)
    question_analytics = models.JSONField(default=dict)
    user_performance = models.JSONField(default=dict)
    
    # Trends and insights
    performance_trends = models.JSONField(default=dict)
    improvement_recommendations = models.JSONField(default=list)
    
    # Report files
    report_pdf = models.FileField(upload_to='reports/', blank=True, null=True)
    report_excel = models.FileField(upload_to='reports/', blank=True, null=True)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    is_automated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"
    
    class Meta:
        db_table = 'results_analyticsreport'
        verbose_name = 'Analytics Report'
        verbose_name_plural = 'Analytics Reports'
        ordering = ['-generated_at']


class UserProgress(models.Model):
    """
    Track individual user progress across multiple tests
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    category = models.ForeignKey('examinations.Category', on_delete=models.CASCADE, related_name='user_progress')
    
    # Progress metrics
    tests_taken = models.PositiveIntegerField(default=0)
    tests_passed = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    best_score = models.FloatField(default=0.0)
    latest_score = models.FloatField(default=0.0)
    
    # Skill development
    skill_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='beginner')
    
    mastery_percentage = models.FloatField(default=0.0)
    
    # Time tracking
    total_study_time = models.PositiveIntegerField(default=0)  # in minutes
    average_test_time = models.FloatField(default=0.0)
    
    # Learning path
    completed_topics = models.JSONField(default=list)
    current_focus_areas = models.JSONField(default=list)
    recommended_next_tests = models.JSONField(default=list)
    
    # Achievements
    achievements = models.JSONField(default=list)
    badges_earned = models.JSONField(default=list)
    streak_count = models.PositiveIntegerField(default=0)  # consecutive days
    
    # Timestamps
    first_attempt_date = models.DateField(blank=True, null=True)
    last_activity_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def update_progress(self):
        """Update progress based on latest test results"""
        attempts = self.user.test_attempts.filter(
            test__category=self.category,
            status='completed'
        ).select_related('result')
        
        if attempts.exists():
            self.tests_taken = attempts.count()
            self.tests_passed = attempts.filter(is_passed=True).count()
            
            scores = [attempt.result.percentage_score for attempt in attempts if hasattr(attempt, 'result')]
            if scores:
                self.average_score = sum(scores) / len(scores)
                self.best_score = max(scores)
                self.latest_score = scores[-1]  # Most recent
            
            # Update skill level based on average score and consistency
            if self.average_score >= 90 and self.tests_passed >= 10:
                self.skill_level = 'expert'
            elif self.average_score >= 80 and self.tests_passed >= 5:
                self.skill_level = 'advanced'
            elif self.average_score >= 70 and self.tests_passed >= 3:
                self.skill_level = 'intermediate'
            else:
                self.skill_level = 'beginner'
            
            # Calculate mastery percentage
            pass_rate = (self.tests_passed / self.tests_taken) * 100 if self.tests_taken > 0 else 0
            self.mastery_percentage = (self.average_score + pass_rate) / 2
            
            # Update dates
            self.first_attempt_date = attempts.first().started_at.date()
            self.last_activity_date = attempts.last().started_at.date()
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} Progress"
    
    class Meta:
        db_table = 'results_userprogress'
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress Records'
        unique_together = ['user', 'category']
        ordering = ['-updated_at']
