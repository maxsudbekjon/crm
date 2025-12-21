from rest_framework import serializers
from apps.models import Lead


# ==========================
# Lead Serializer
# ==========================
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from apps.models.leads import Lead


class LeadSerializer(serializers.ModelSerializer):
    time_label = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            'id',
            'full_name',
            'phone',
            'time_label',
        )

    def get_time_label(self, obj):
        today = timezone.now().date()
        created_date = obj.created_at.date()

        if created_date == today:
            return "Bugun"
        elif created_date == today - timedelta(days=1):
            return "Kecha"
        elif created_date >= today - timedelta(days=7):
            return "1 hafta oldin"
        else:
            return created_date.strftime("%d.%m.%Y")



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
