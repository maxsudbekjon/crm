from rest_framework import serializers
from apps.models.task_model import Task


class TaskSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    course_name = serializers.CharField(source='lead.course.title', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'lead',
            'lead_name',
            'course_name',
            'title',
            'description',
            'deadline',
            'is_completed',
            'completed_at',
        ]
        ref_name = "TaskSerializerTopshiriq"