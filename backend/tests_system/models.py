from django.db import models
from django.contrib.auth.models import User

class SkillTest(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('react', 'React'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.language})"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('code', 'Code Challenge'),
    ]

    test = models.ForeignKey(SkillTest, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    text = models.TextField()
    order = models.IntegerField(default=0)

    # For quiz
    option_a = models.CharField(max_length=255, blank=True, default='')
    option_b = models.CharField(max_length=255, blank=True, default='')
    option_c = models.CharField(max_length=255, blank=True, default='')
    option_d = models.CharField(max_length=255, blank=True, default='')
    correct_answer = models.CharField(max_length=1, blank=True, default='')  # a, b, c, d

    # For code challenge
    code_template = models.TextField(blank=True, default='')
    test_code = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.test.title} - Q{self.order}"


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(SkillTest, on_delete=models.CASCADE, related_name='results')

    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=100)
    status = models.CharField(max_length=20, choices=[
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], default='failed')

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}: {self.score}/{self.max_score}"


class Answer(models.Model):
    result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.result.user.username} - Q{self.question.order}"


class CodeSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'All Tests Passed'),
        ('failed', 'Some Tests Failed'),
        ('error', 'Execution Error'),
        ('timeout', 'Timeout'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_submissions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    output = models.TextField(blank=True, default='')
    test_results = models.JSONField(default=list, blank=True)
    tests_passed = models.IntegerField(default=0)
    tests_total = models.IntegerField(default=0)
    execution_time_ms = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.question} [{self.status}]"
