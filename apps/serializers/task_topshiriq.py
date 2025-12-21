from rest_framework import serializers
from apps.models.task_model import Task

class TaskSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    course_name = serializers.SerializerMethodField()

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

    def get_course_name(self, obj):
        if obj.lead and obj.lead.course:
            return obj.lead.course.title
        return None
