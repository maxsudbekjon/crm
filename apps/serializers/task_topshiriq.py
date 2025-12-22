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
        # 🔹 Swagger render paytida DB chaqirmaslik
        if self.context.get('swagger_fake_view', False):
            return None

        lead = getattr(obj, 'lead', None)
        if not lead:
            return None

        course = getattr(lead, 'course', None)
        if not course:
            return None

        return getattr(course, 'title', None)
