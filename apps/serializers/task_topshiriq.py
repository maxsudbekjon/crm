from rest_framework import serializers
from apps.models.task_model import Task


# task_topshiriq.py
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        ref_name = "TaskTopshiriqSerializer"
