from django.db.models import Sum
from django.utils.timezone import localtime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from apps.models.call import Call
from apps.serializers.call_qongiroq import CallSerializer


# ===== API VIEW =====
class MyCallsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        operator = getattr(user, "operator", None)

        if not operator:
            return Response({
                "cards": {
                    "jami": 0,
                    "chiquvchi": 0,
                    "otkazib_yuborilgan": 0,
                    "jami_vaqt": "0 min 0 sek"
                },
                "calls": []
            })

        calls = Call.objects.filter(operator=operator).select_related("lead").order_by("-call_time")

        # ===== CARDS =====
        jami = calls.count()
        chiquvchi = calls.filter(result=Call.CallResult.SUCCESSFUL).count()
        otkazib_yuborilgan = calls.filter(result__in=[
            Call.CallResult.NO_ANSWER,
            Call.CallResult.BUSY,
            Call.CallResult.FAILED
        ]).count()

        jami_vaqt_seconds = calls.aggregate(total=Sum("duration_seconds"))["total"] or 0
        jami_vaqt = f"{jami_vaqt_seconds // 60} min {jami_vaqt_seconds % 60} sek"

        # ===== CALLS =====
        serializer = CallSerializer(calls, many=True)

        return Response({
            "cards": {
                "jami": jami,
                "chiquvchi": chiquvchi,
                "otkazib_yuborilgan": otkazib_yuborilgan,
                "jami_vaqt": jami_vaqt
            },
            "calls": serializer.data
        })