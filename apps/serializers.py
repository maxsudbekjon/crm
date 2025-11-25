from rest_framework import serializers
from .models import Lead, Task, Operator, Notification
from Auth.serializers import *
from rest_framework.parsers import MultiPartParser, FormParser

# ==========================
# Lead Serializer
# ==========================
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'full_name', 'phone', 'status', 'operator', 'created_at', 'updated_at']
        read_only_fields = ['id', 'operator', 'created_at', 'updated_at']


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'full_name', 'phone', 'operator']


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
            raise serializers.ValidationError("Siz faqat o‘zingizga biriktirilgan leadni yangilashingiz mumkin.")
        return attrs


# ==========================
# Operator Serializer
# =========================
class OperatorSerializer(serializers.ModelSerializer):
    user = RegisterSerializer()
    # photo = serializers.ImageField(required=False)

    class Meta:
        model = Operator
        fields = [
            'id', 'user', 'status',
            'salary', 'penalty', 'gender', 'branch'
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = RegisterSerializer().create(user_data)
        operator = Operator.objects.create(user=user, **validated_data)
        return operator


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user'] = {
            "id": instance.user.id,
            "username": instance.user.username,
            "full_name": instance.user.first_name + " " + instance.user.last_name
        }
        rep['branch'] = instance.branch.name if instance.branch else None
        # rep['photo'] = instance.photo.url if instance.photo else None
        return rep


# ==========================
# Task Serializer
# ==========================
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'operator', 'lead', 'title', 'description', 'deadline',
                  'is_completed', 'completed_at', 'penalty_points']
        read_only_fields = ['id', 'operator', 'is_completed', 'completed_at']


class NotificationSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'message', 'data', 'is_read', 'created_at', 'operator_name']


