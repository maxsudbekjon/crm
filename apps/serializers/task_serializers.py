from rest_framework import serializers
from apps.models import Task, Notification


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'operator', 'lead', 'title', 'description', 'deadline',
                  'is_completed', 'completed_at']
        read_only_fields = ['id', 'operator', 'is_completed', 'completed_at']


class NotificationSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'message', 'data', 'is_read', 'created_at', 'operator_name']

