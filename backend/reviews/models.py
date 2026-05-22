from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class CompanyReview(models.Model):
    company_name = models.CharField(max_length=255, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    is_anonymous = models.BooleanField(default=False)

    rating_overall = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_work_life = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_career_growth = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_salary = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_management = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    title = models.CharField(max_length=255)
    pros = models.TextField(help_text='What is good about working here')
    cons = models.TextField(help_text='What could be improved')
    advice = models.TextField(blank=True, default='', help_text='Advice for management')

    is_current_employee = models.BooleanField(default=False)
    position = models.CharField(max_length=255, blank=True, default='')

    is_approved = models.BooleanField(default=True)

    helpful_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['author', 'company_name']

    def __str__(self):
        return f"Review of {self.company_name} by {self.author.username}"

    @property
    def average_rating(self):
        return round(
            (self.rating_overall + self.rating_work_life + self.rating_career_growth
             + self.rating_salary + self.rating_management) / 5, 1
        )


class ReviewHelpful(models.Model):
    review = models.ForeignKey(CompanyReview, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='helpful_votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['review', 'user']

    def __str__(self):
        return f"{self.user.username} -> review #{self.review.id}"
