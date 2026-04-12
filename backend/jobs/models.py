from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    LEVEL_CHOICES = [
        ('junior', 'Junior'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    salary_min = models.IntegerField(null=True, blank=True, help_text='Min salary in KZT')
    salary_max = models.IntegerField(null=True, blank=True, help_text='Max salary in KZT')

    # Level and requirements
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='junior')
    requirements_text = models.TextField(help_text='Free text requirements from HR')
    training_provided = models.BooleanField(default=False)
    experience_years = models.IntegerField(default=0, help_text='Required years of experience')
    is_remote = models.BooleanField(default=False)

    # Technologies
    tech_stack = models.JSONField(default=list, help_text='List of technologies, e.g. ["Python", "Django"]')

    # Analyzer fields (filled by analytics module)
    detected_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, blank=True, default='')
    is_overqualified = models.BooleanField(default=False)
    honesty_score = models.IntegerField(default=100, help_text='0-100, how honest are the requirements')
    parsed_skills = models.JSONField(default=list, blank=True, help_text='Skills extracted by analyzer')

    # Posted by
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company}"


class JobTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    jobs = models.ManyToManyField(Job, related_name='tags', blank=True)

    def __str__(self):
        return self.name
