from rest_framework import serializers
from .models import Lead, Task, Operator


# ============================
# LEAD SERIALIZERS
# ============================
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'full_name', 'phone', 'status', 'operator', 'created_at', 'updated_at']
        read_only_fields = ['id', 'operator', 'created_at', 'updated_at']

class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['full_name', 'phone', 'source']

from django import forms
from .models import Enrollment

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student_name', 'course', 'operator', 'price_paid']


class LeadStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['status']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            raise serializers.ValidationError("Login qilishingiz kerak!")

        lead = self.instance
        operator = getattr(request.user, 'operator', None)

        if lead.operator != operator:
            raise serializers.ValidationError(
                "Siz faqat o‘zingizga biriktirilgan leadni yangilashingiz mumkin."
            )
        return attrs


# ============================
# OPERATOR SERIALIZER
# ============================
from rest_framework import serializers
from .models import Operator

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'

    def create(self, validated_data):
        return Operator.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.status = validated_data.get('status', instance.status)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.salary = validated_data.get('salary', instance.salary)
        instance.penalty = validated_data.get('penalty', instance.penalty)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.save()
        return instance

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['lead', 'title', 'description', 'deadline']

# ============================
# TASK SERIALIZER
# ============================
class TaskSerializer(serializers.ModelSerializer):
    """Task ma’lumotlarini o‘qish va yozish uchun serializer"""

    class Meta:
        model = Task
        fields = [
            'id', 'operator', 'lead', 'title',
            'description', 'deadline', 'is_completed',
            'completed_at', 'penalty_points'
        ]
        read_only_fields = ['completed_at']