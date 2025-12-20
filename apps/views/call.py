from celery.worker.state import total_count
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Call, Operator
from apps.serializers.call import CallListSerializer

def format_duration(seconds: int) -> str:
    if not seconds:
        return "0 sek"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []

    if hours > 0:
        parts.append(f"{hours} soat")
    if minutes > 0:
        parts.append(f"{minutes} min")
    if secs > 0:
        parts.append(f"{secs} sek")

    return " ".join(parts)


class MyCallsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            operator = Operator.objects.get(user=request.user)
        except Operator.DoesNotExist:
            return Response(
                {"detail": "Siz operator emassiz"},
                status=403
            )

        calls = Call.objects.filter(operator=operator)

        total_seconds = calls.aggregate(
            total=Sum("duration_seconds")
        )["total"] or 0

        # 🔹 SUMMARY
        summary = {
            "jami": calls.count(),
            "chiquvchi": calls.filter(
                result=Call.CallResult.SUCCESSFUL
            ).count(),
            "otkazib_yuborilgan": calls.filter(
                result__in=[
                    Call.CallResult.NO_ANSWER,
                    Call.CallResult.FAILED
                ]
            ).count(),
            "jami_vaqt": format_duration(total_seconds)
        }

        # 🔹 LIST
        serializer = CallListSerializer(calls, many=True)

        return Response({
            "summary": summary,
            "calls": serializer.data
        })
