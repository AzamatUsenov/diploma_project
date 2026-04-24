from django.db.models.signals import post_save
from django.dispatch import receiver
from applications.models import Application, Message
from .models import Notification


@receiver(post_save, sender=Application)
def notify_application_status_change(sender, instance, created, **kwargs):
    """Уведомление при изменении статуса заявки"""
    if not created and instance.tracker.has_changed('status'):
        # Уведомляем соискателя
        Notification.objects.create(
            user=instance.applicant,
            notification_type='application_status',
            title=f'Статус заявки изменен: {instance.job.title}',
            message=f'Ваша заявка на вакансию "{instance.job.title}" теперь имеет статус: {instance.get_status_display()}',
            link=f'/applications/'
        )


@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    """Уведомление о новом сообщении в чате"""
    if created:
        # Определяем получателя (не отправителя)
        application = instance.application

        if instance.sender == application.applicant:
            # Отправитель - соискатель, уведомляем HR
            recipient = application.job.posted_by
        else:
            # Отправитель - HR, уведомляем соискателя
            recipient = application.applicant

        Notification.objects.create(
            user=recipient,
            notification_type='new_message',
            title=f'Новое сообщение от {instance.sender.username}',
            message=instance.text[:100] + ('...' if len(instance.text) > 100 else ''),
            link=f'/applications/{application.id}/chat/'
        )
