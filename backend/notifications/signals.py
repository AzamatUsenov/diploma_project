from django.db.models.signals import post_save
from django.dispatch import receiver
from applications.models import Application, Message
from tests_system.models import TestResult
from .models import Notification


@receiver(post_save, sender=Application)
def notify_on_application(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.job.posted_by,
            notification_type='new_application',
            title='Новый отклик',
            message=f'{instance.applicant.username} откликнулся на "{instance.job.title}"',
            link=f'/applications/{instance.id}/',
        )
    elif instance.status in ('accepted', 'rejected'):
        status_text = 'принят' if instance.status == 'accepted' else 'отклонён'
        Notification.objects.create(
            user=instance.applicant,
            notification_type='application_status',
            title='Статус отклика изменён',
            message=f'Ваш отклик на "{instance.job.title}" {status_text}',
            link=f'/applications/{instance.id}/',
        )


@receiver(post_save, sender=Message)
def notify_on_message(sender, instance, created, **kwargs):
    if not created:
        return
    application = instance.application
    recipient = (
        application.job.posted_by
        if instance.sender == application.applicant
        else application.applicant
    )
    Notification.objects.create(
        user=recipient,
        notification_type='new_message',
        title='Новое сообщение',
        message=f'{instance.sender.username}: {instance.text[:100]}',
        link=f'/applications/{application.id}/chat/',
    )


@receiver(post_save, sender=TestResult)
def notify_on_test_result(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.completed_at is None:
        return
    status_text = 'пройден' if instance.status == 'passed' else 'не пройден'
    Notification.objects.create(
        user=instance.user,
        notification_type='test_result',
        title='Результат теста',
        message=f'Тест "{instance.test.title}" {status_text} ({instance.score}/{instance.max_score})',
        link=f'/tests/results/{instance.id}/',
    )
