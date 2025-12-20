from rest_framework import serializers
from apps.models.task_model import Task

class TaskSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    course_name = serializers.SerializerMethodField()  # course_name uchun getter qo‘shildi

    class Meta:
        model = Task
        fields = [
            'id',
            'operator',
            'lead',
            'lead_name',
            'course_name',  # ✅ Meta.fields ichida bo‘lishi shart
            'title',
            'description',
            'deadline',
            'is_completed',
            'completed_at',
        ]
        ref_name = "TaskSerializerTopshiriq"  # ✅ unique ref_name


    def get_course_name(self, obj):
        if obj.lead and obj.lead.course:
            return obj.lead.course.title  # <-- 'name' o‘rniga 'title' ishlatildi
        return None