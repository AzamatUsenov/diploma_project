from rest_framework import serializers
from .models import Notification, UserActivity


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'link',
                  'is_read', 'created_at', 'time_ago']
        read_only_fields = ['created_at']

    def get_time_ago(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.created_at

        if delta.days > 0:
            return f'{delta.days}д назад'
        elif delta.seconds > 3600:
            return f'{delta.seconds // 3600}ч назад'
        elif delta.seconds > 60:
            return f'{delta.seconds // 60}м назад'
        else:
            return 'только что'


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['id', 'activity_type', 'related_object_id',
                  'related_object_type', 'metadata', 'created_at']
        read_only_fields = ['created_at']
