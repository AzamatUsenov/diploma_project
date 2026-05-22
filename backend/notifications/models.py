from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('application_status', 'Application Status'),
        ('new_message', 'New Message'),
        ('job_recommendation', 'Job Recommendation'),
        ('test_result', 'Test Result'),
        ('new_application', 'New Application'),
        ('new_review', 'New Review'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, default='')
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    @property
    def time_ago(self):
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        seconds = delta.total_seconds()
        if seconds < 60:
            return 'только что'
        elif seconds < 3600:
            mins = int(seconds // 60)
            return f'{mins} мин. назад'
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f'{hours} ч. назад'
        else:
            days = int(seconds // 86400)
            return f'{days} дн. назад'
