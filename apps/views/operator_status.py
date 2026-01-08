from django.db.models import Count, Q, F, FloatField, Sum, ExpressionWrapper
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.models.operator import Operator
from apps.models.leads import Lead
from apps.serializers.operator_status import OperatorStatsSerializer


class OperatorStatsAPIView(ListAPIView):
    """
    Operatorlar statistikasi API:
    - leads_count: operatorga tegishli barcha leadlar soni
    - sold_count: sotilgan leadlar soni
    - revenue: sotilgan leadlar bo‘yicha daromad (course price * commission_rate)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OperatorStatsSerializer

    def get_queryset(self):
        return (
            Operator.objects
            .select_related("user")
            .filter(user__role="operator")
            .annotate(
                leads_count=Count("leads", distinct=True),

                sold_count=Count(
                    "leads",
                    filter=Q(leads__status=Lead.Status.SOLD),
                    distinct=True
                ),

                revenue=Sum(
                    ExpressionWrapper(
                        F("leads__course__price") * F("commission_rate"),
                        output_field=FloatField()
                    ),
                    filter=Q(
                        leads__status=Lead.Status.SOLD,
                        leads__course__isnull=False
                    )
                )
            )
            .order_by("-sold_count")
        )
