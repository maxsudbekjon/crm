# serializers.py
from rest_framework import serializers

from apps.models import Call


class CallListSerializer(serializers.ModelSerializer):
    lead = serializers.CharField(source="lead.full_name")
    turi = serializers.SerializerMethodField()
    davomiyligi = serializers.SerializerMethodField()
    vaqt = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = [
            "id",
            "lead",
            "turi",
            "davomiyligi",
            "vaqt",
            "notes"
        ]

    def get_turi(self, obj):
        if obj.result == Call.CallResult.SUCCESSFUL:
            return "Chiquvchi"
        return "O‘tkazib yuborilgan"

    def get_davomiyligi(self, obj):
        minutes = obj.duration_seconds // 60
        seconds = obj.duration_seconds % 60
        return f"{minutes} min {seconds} sek"

    def get_vaqt(self, obj):
        return obj.call_time.strftime("MO1 %d %H:%M")
