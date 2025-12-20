from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.models.call import Call
from apps.serializers.call_qongiroq import CallSerializer

class CallsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Admin/direktor barcha operatorlar qo‘ng‘iroqlarini ko‘radi
        if user.role == "admin":
            calls = Call.objects.all().select_related("lead", "operator").order_by("-call_time")
        else:
            # Operator faqat o‘z qo‘ng‘iroqlarini ko‘radi
            calls = Call.objects.filter(operator=user).select_related("lead", "operator").order_by("-call_time")

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