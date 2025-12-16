from django.db.models import Sum
from django.utils.timezone import localtime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from apps.models.call import Call


# ===== SERIALIZER =====
class CallSerializer(serializers.ModelSerializer):
    lead = serializers.CharField(source="lead.full_name")
    turi = serializers.SerializerMethodField()
    davomiyligi = serializers.SerializerMethodField()
    vaqt = serializers.SerializerMethodField()
    izoh = serializers.CharField(source="notes", default="")

    class Meta:
        model = Call
        fields = ["lead", "turi", "davomiyligi", "vaqt", "izoh"]

    def get_turi(self, obj):
        return "Chiquvchi" if obj.result == Call.CallResult.SUCCESSFUL else "O‘tkazib yuborilgan"

    def get_davomiyligi(self, obj):
        minutes = obj.duration_seconds // 60
        seconds = obj.duration_seconds % 60
        return f"{minutes} min {seconds} sek"

    def get_vaqt(self, obj):
        return localtime(obj.call_time).strftime("%m %d %H:%M")