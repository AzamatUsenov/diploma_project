import uuid
from django.db import models
from django.contrib.auth.models import User
from tests_system.models import Question


class LiveSession(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for candidate'),
        ('active', 'In progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hr = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_sessions')
    candidate = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidate_sessions')
    title = models.CharField(max_length=255)
    questions = models.ManyToManyField(Question, blank=True, related_name='live_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    time_limit_minutes = models.IntegerField(default=30)

    invite_code = models.CharField(max_length=8, unique=True, blank=True)
    candidate_code = models.TextField(blank=True, default='')
    current_question_index = models.IntegerField(default=0)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session {self.invite_code} by {self.hr.username}"


class SessionResult(models.Model):
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='results')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.CharField(max_length=20, default='not_submitted')
    tests_passed = models.IntegerField(default=0)
    tests_total = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['submitted_at']
