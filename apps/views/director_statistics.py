from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.DirectorStatisticsService import DirectorStatisticsService

class DirectorStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='period',
                in_=openapi.IN_QUERY,
                description=(
                    "Filter statistics by period:\n"
                    "- today → Bugungi ma'lumotlar\n"
                    "- week → Shu haftalik ma'lumotlar\n"
                    "- month → Shu oylik ma'lumotlar (default)"
                ),
                type=openapi.TYPE_STRING,
                enum=['today', 'week', 'month'],
                default='month',
                required=False
            )
        ]
    )
    def get(self, request):
        period = request.query_params.get("period", "month")

        data = {
            "revenue_dynamic": DirectorStatisticsService.revenue_last_6_months(),
            "sellers_performance": DirectorStatisticsService.sellers_performance(period),
            "conversion_funnel": DirectorStatisticsService.conversion_funnel(period),
            "average_deal_value": DirectorStatisticsService.average_deal_value(
                date.today().replace(day=1)
            ),
            "sales_cycle": DirectorStatisticsService.sales_cycle(
                date.today().replace(day=1)
            ),
            "retention": DirectorStatisticsService.retention(
                date.today().replace(day=1)
            ),
        }

        return Response(data)
