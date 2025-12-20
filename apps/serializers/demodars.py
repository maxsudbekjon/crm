from rest_framework import serializers
from apps.models.demodars import DemoLesson, LeadDemoAssignment

class DemoLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoLesson
        fields = ['id', 'course', 'teacher', 'start_at', 'is_active']


class LeadDemoAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadDemoAssignment
        fields = ['id', 'lead', 'demo', 'assigned_by', 'assigned_at']
        read_only_fields = ['assigned_by', 'assigned_at']

    def create(self, validated_data):
        # assigned_by ni request user bilan to‘ldiramiz
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)