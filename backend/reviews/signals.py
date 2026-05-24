from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import UserProfile
from notifications.models import Notification
from .models import CompanyReview


@receiver(post_save, sender=CompanyReview)
def notify_hr_on_review(sender, instance, created, **kwargs):
    if not created:
        return
    hr_profiles = UserProfile.objects.filter(
        role='hr',
        company_name__iexact=instance.company_name,
    ).select_related('user')

    for profile in hr_profiles:
        if profile.user == instance.author:
            continue
        Notification.objects.create(
            user=profile.user,
            notification_type='new_review',
            title='Новый отзыв о компании',
            message=f'Пользователь оставил отзыв "{instance.title}" о {instance.company_name}',
            link=f'/reviews/?company={instance.company_name}',
        )
