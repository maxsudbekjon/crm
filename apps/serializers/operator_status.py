from rest_framework import serializers
from apps.models.operator import Operator


class OperatorStatsSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name")
    email = serializers.EmailField(source="user.email")
    phone = serializers.CharField(source="user.phone")

    leads_count = serializers.IntegerField()
    sold_count = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    conversion = serializers.SerializerMethodField()

    class Meta:
        model = Operator
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "status",      # lavozim
            "leads_count",
            "sold_count",
            "conversion",
            "revenue",
        )

    def get_conversion(self, obj):
        if obj.leads_count == 0:
            return 0
        return round((obj.sold_count / obj.leads_count) * 100)

from rest_framework import serializers

class OperatorDataSerializer(serializers.Serializer):
    xodim = serializers.CharField()
    ish_boshlangan = serializers.CharField()
    lavozim = serializers.CharField()
    lead = serializers.IntegerField()
    sotilgan = serializers.IntegerField()
    konversiya = serializers.FloatField()
    daromad = serializers.FloatField()