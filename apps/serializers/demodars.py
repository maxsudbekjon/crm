from rest_framework import serializers, permissions
from apps.models.demodars import DemoLesson, LeadDemoAssignment
from apps.models.leads import Lead  # Lead modelini import qilamiz


from rest_framework import serializers
from apps.models.demodars import DemoLesson

class DemoLessonSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)  # yoki .username
    course_title = serializers.CharField(source='course.title', read_only=True)  # course nomi

    class Meta:
        model = DemoLesson
        fields = ['id', 'course', 'course_title', 'teacher', 'teacher_name', 'start_at', 'is_active']
        read_only_fields = ['teacher_name', 'course_title']  # Swagger-da qulufcha chiqadi



class LeadDemoAssignmentSerializer(serializers.ModelSerializer):
    permission_classes = [permissions.IsAuthenticated]

    lead_name = serializers.CharField(source='lead.name', read_only=True)  # lead nomi

    class Meta:
        model = LeadDemoAssignment
        fields = ['id', 'lead', 'lead_name', 'demo', 'assigned_by', 'assigned_at']
        read_only_fields = ['assigned_by', 'assigned_at']

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)
