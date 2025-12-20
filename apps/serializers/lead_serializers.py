from rest_framework import serializers
from apps.models import Lead


# ==========================
# Lead Serializer
# ==========================
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = ['operator']

    def update(self, instance, validated_data):
        # operator faqat birinchi yaratishda belgilanadi
        validated_data["operator"] = instance.operator
        return super().update(instance, validated_data)


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['full_name', 'phone', 'source']


class LeadStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['status']

    def validate(self, attrs):
        new_status = attrs.get("status")
        lead = self.instance

        # agar status 'sold' bo‘lsa → leadda payment bo‘lishi shart
        if new_status == Lead.Status.SOLD:
            if not lead.payments.exists():
                raise serializers.ValidationError(
                    {"status": "Lead uchun to‘lov mavjud emas. Sold qilish taqiqlanadi."}
                )

        return attrs

class LeadSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"