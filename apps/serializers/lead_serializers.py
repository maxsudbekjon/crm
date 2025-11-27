from rest_framework import serializers
from apps.models import Lead


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

