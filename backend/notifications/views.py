from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Notification, UserActivity
from .serializers import NotificationSerializer, UserActivitySerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Количество непрочитанных уведомлений"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Пометить все как прочитанные"""
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'marked_read': updated})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Пометить одно уведомление как прочитанное"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked_read'})


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """История активности пользователя"""
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика активности"""
        user = request.user
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Подсчет активности
        activity_today = UserActivity.objects.filter(
            user=user,
            created_at__date=today
        ).count()

        activity_week = UserActivity.objects.filter(
            user=user,
            created_at__date__gte=week_ago
        ).count()

        activity_month = UserActivity.objects.filter(
            user=user,
            created_at__date__gte=month_ago
        ).count()

        # Топ активностей
        top_activities = UserActivity.objects.filter(
            user=user
        ).values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        return Response({
            'today': activity_today,
            'this_week': activity_week,
            'this_month': activity_month,
            'top_activities': list(top_activities)
        })

    @action(detail=False, methods=['post'])
    def track(self, request):
        """Отслеживание активности (вызывается из фронтенда)"""
        activity_type = request.data.get('activity_type')
        related_id = request.data.get('related_object_id')
        related_type = request.data.get('related_object_type')
        metadata = request.data.get('metadata', {})

        UserActivity.objects.create(
            user=request.user,
            activity_type=activity_type,
            related_object_id=related_id,
            related_object_type=related_type,
            metadata=metadata
        )

        return Response({'status': 'tracked'})
