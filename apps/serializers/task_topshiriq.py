from rest_framework import serializers
from apps.models import Lead
from apps.models.task_model import Task

class LeadSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True, default='-')  # course bo'sh bo'lsa '-'

    class Meta:
        model = Lead
        fields = ['id', 'name', 'course_name']

class TaskSerializer(serializers.ModelSerializer):
    lead = LeadSerializer(read_only=True)  # nested serializer ishlaydi
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    course_name = serializers.CharField(source='lead.course.name', read_only=True, default='-')

    class Meta:
        model = Task
        fields = [
            'id', 'operator', 'lead', 'title', 'description',
            'deadline', 'is_completed', 'completed_at',
            'lead_name', 'course_name'
        ]
