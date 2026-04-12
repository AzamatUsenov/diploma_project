from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('applicant', 'Applicant'),
        ('hr', 'HR Manager'),
    ]

    LEVEL_CHOICES = [
        ('junior', 'Junior'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='applicant')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='junior', blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, default='')
    skills = models.JSONField(default=list, blank=True, help_text='List of known skills, e.g. ["Python", "Django", "Git"]')

    # For applicant
    portfolio_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')

    # For HR
    company_name = models.CharField(max_length=255, blank=True, default='')
    company_description = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
