from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from apps.models.leads import Lead
from apps.models.operator import Operator
from apps.serializers.lead_serializers import LeadSerializer

PERIOD_CHOICES = [
    "barchasi",
    "bugun",
    "kecha",
    "3kun_oldin",
    "1xafta_oldin",
    "1oy_oldin"
]


class LeadFilterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def filter_by_period(self, queryset, period):
        today = timezone.now().date()

        if period == "bugun":
            return queryset.filter(created_at__date=today)
        if period == "kecha":
            yesterday = today - timedelta(days=1)
            return queryset.filter(created_at__date=yesterday)
        if period == "3kun_oldin":
            start_date = today - timedelta(days=3)
            end_date = today
            return queryset.filter(created_at__date__range=(start_date, end_date))
        if period == "1xafta_oldin":
            start_date = today - timedelta(days=7)
            end_date = today
            return queryset.filter(created_at__date__range=(start_date, end_date))
        if period == "1oy_oldin":
            start_date = today - timedelta(days=30)
            end_date = today
            return queryset.filter(created_at__date__range=(start_date, end_date))
        if period == "barchasi":
            return queryset

        return queryset.none()  # Noto‘g‘ri period

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="period",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                enum=PERIOD_CHOICES,
                description="Vaqt bo‘yicha filter"
            ),
        ]
    )
    def get(self, request):
        period = request.query_params.get("period", "barchasi")
        user = request.user

        # 🔐 Base queryset
        if user.is_staff:
            leads_qs = Lead.objects.all()
        else:
            try:
                leads_qs = Lead.objects.filter(operator=user.operator)
            except Operator.DoesNotExist:
                return Response({"detail": "Siz operator emassiz"}, status=403)

        # ⏱ Period filter
        if period not in PERIOD_CHOICES:
            leads_qs = Lead.objects.none()
        else:
            leads_qs = self.filter_by_period(leads_qs, period)

        # ✅ Response
        return Response({
            "period": period,
            "count": leads_qs.count(),
            "leads": LeadSerializer(leads_qs, many=True).data
        })
