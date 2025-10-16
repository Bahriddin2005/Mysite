from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Question(models.Model):
    """
    Individual question in a test
    """
    QUESTION_TYPES = (
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('numeric', 'Numeric Answer'),
        ('text', 'Text Answer'),
        ('matching', 'Matching/Pairing'),
        ('essay', 'Essay'),
    )
    
    DIFFICULTY_LEVELS = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    # Basic information
    test = models.ForeignKey('examinations.Test', on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    
    # Content
    text = models.TextField(help_text="The question text")
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
    
    # Scoring and difficulty
    points = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    
    # Ordering and timing
    order = models.PositiveIntegerField(default=0)
    time_limit = models.PositiveIntegerField(blank=True, null=True, help_text="Time limit for this question in seconds")
    
    # Settings for specific question types
    # For numeric questions
    numeric_answer = models.FloatField(blank=True, null=True)
    numeric_tolerance = models.FloatField(default=0.0, help_text="Acceptable margin of error")
    
    # For matching questions
    matching_pairs = models.JSONField(default=dict, blank=True, help_text="Correct pairs for matching questions")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_questions')
    
    # Statistics (denormalized)
    times_answered = models.PositiveIntegerField(default=0)
    times_correct = models.PositiveIntegerField(default=0)
    average_time_spent = models.FloatField(default=0.0)  # in seconds
    
    @property
    def success_rate(self):
        if self.times_answered == 0:
            return 0
        return (self.times_correct / self.times_answered) * 100
    
    @property
    def is_auto_gradable(self):
        return self.question_type in ['single_choice', 'multiple_choice', 'true_false', 'numeric', 'matching']
    
    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}..."
    
    class Meta:
        db_table = 'questions_question'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['test', 'order']
        unique_together = ['test', 'order']


class Choice(models.Model):
    """
    Answer choices for multiple choice questions
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, help_text="Explanation for this choice")
    order = models.PositiveIntegerField(default=0)
    
    # For matching questions - used as items to match
    match_key = models.CharField(max_length=50, blank=True, help_text="Key for matching questions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.text[:30]}... ({'✓' if self.is_correct else '✗'})"
    
    class Meta:
        db_table = 'questions_choice'
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'
        ordering = ['question', 'order']


class QuestionAnswer(models.Model):
    """
    User's answer to a specific question
    """
    # Relations
    attempt = models.ForeignKey('examinations.TestAttempt', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    
    # Answer data
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name='selected_in_answers')
    text_answer = models.TextField(blank=True)
    numeric_answer = models.FloatField(blank=True, null=True)
    matching_pairs = models.JSONField(default=dict, blank=True)  # For matching questions
    
    # Grading
    is_correct = models.BooleanField(default=False)
    points_awarded = models.FloatField(default=0.0)
    
    # Manual grading (for essay/text questions)
    manually_graded = models.BooleanField(default=False)
    grader_feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='graded_answers')
    graded_at = models.DateTimeField(blank=True, null=True)
    
    # Timing and behavior
    time_spent = models.PositiveIntegerField(default=0, help_text="Time spent on this question in seconds")
    answer_changed_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    first_answered_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-grade if possible
        if not self.manually_graded and self.question.is_auto_gradable:
            self.auto_grade()
        super().save(*args, **kwargs)
    
    def auto_grade(self):
        """
        Automatically grade the answer based on question type
        """
        question = self.question
        
        if question.question_type == 'single_choice':
            correct_choices = question.choices.filter(is_correct=True)
            selected_choices = self.selected_choices.all()
            
            if (len(selected_choices) == 1 and 
                len(correct_choices) == 1 and 
                selected_choices[0] in correct_choices):
                self.is_correct = True
                self.points_awarded = question.points
            else:
                self.is_correct = False
                self.points_awarded = 0
                
        elif question.question_type == 'multiple_choice':
            correct_choices = set(question.choices.filter(is_correct=True))
            selected_choices = set(self.selected_choices.all())
            
            if correct_choices == selected_choices:
                self.is_correct = True
                self.points_awarded = question.points
            else:
                # Partial credit calculation
                if selected_choices.issubset(correct_choices):
                    ratio = len(selected_choices) / len(correct_choices)
                    self.points_awarded = question.points * ratio
                else:
                    self.points_awarded = 0
                self.is_correct = False
                
        elif question.question_type == 'true_false':
            correct_choice = question.choices.filter(is_correct=True).first()
            selected_choice = self.selected_choices.first()
            
            if selected_choice == correct_choice:
                self.is_correct = True
                self.points_awarded = question.points
            else:
                self.is_correct = False
                self.points_awarded = 0
                
        elif question.question_type == 'numeric':
            if (self.numeric_answer is not None and 
                question.numeric_answer is not None):
                
                difference = abs(self.numeric_answer - question.numeric_answer)
                if difference <= question.numeric_tolerance:
                    self.is_correct = True
                    self.points_awarded = question.points
                else:
                    self.is_correct = False
                    self.points_awarded = 0
                    
        elif question.question_type == 'matching':
            correct_pairs = question.matching_pairs
            user_pairs = self.matching_pairs
            
            if correct_pairs == user_pairs:
                self.is_correct = True
                self.points_awarded = question.points
            else:
                # Partial credit for correct matches
                correct_count = sum(1 for k, v in user_pairs.items() 
                                  if correct_pairs.get(k) == v)
                total_pairs = len(correct_pairs)
                if total_pairs > 0:
                    self.points_awarded = question.points * (correct_count / total_pairs)
                else:
                    self.points_awarded = 0
                self.is_correct = correct_count == total_pairs
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.text[:30]}..."
    
    class Meta:
        db_table = 'questions_questionanswer'
        verbose_name = 'Question Answer'
        verbose_name_plural = 'Question Answers'
        unique_together = ['attempt', 'question']


class QuestionStatistics(models.Model):
    """
    Aggregated statistics for questions
    """
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='statistics')
    
    # Performance metrics
    total_attempts = models.PositiveIntegerField(default=0)
    correct_attempts = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    
    # Time metrics
    average_time_spent = models.FloatField(default=0.0)  # seconds
    median_time_spent = models.FloatField(default=0.0)
    
    # Difficulty analysis
    discrimination_index = models.FloatField(default=0.0)  # How well question separates high/low performers
    difficulty_index = models.FloatField(default=0.0)  # Percentage who got it right
    
    # Choice analysis (for MC questions)
    choice_distribution = models.JSONField(default=dict)  # How many chose each option
    
    # Metadata
    last_calculated = models.DateTimeField(auto_now=True)
    
    @property
    def success_rate(self):
        if self.total_attempts == 0:
            return 0
        return (self.correct_attempts / self.total_attempts) * 100
    
    def __str__(self):
        return f"Stats for: {self.question.text[:30]}..."
    
    class Meta:
        db_table = 'questions_questionstatistics'
        verbose_name = 'Question Statistics'
        verbose_name_plural = 'Question Statistics'
