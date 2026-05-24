from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'link', 'is_read', 'time_ago', 'created_at',
        ]
        read_only_fields = ['id', 'notification_type', 'title', 'message', 'link', 'created_at']
