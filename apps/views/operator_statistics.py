from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date
from apps.operator_statistics import OperatorStatisticsService
from apps.permissions import IsOperator

class OperatorStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOperator]

    def get(self, request):
        if not hasattr(request.user, "operator"):
            return Response(
                {"detail": "Operator profili topilmadi"},
                status=403
            )

        operator = request.user.operator
        month = request.query_params.get("month")

        if month:
            month_date = date.fromisoformat(month + "-01")
        else:
            today = date.today()
            month_date = today.replace(day=1)

        return Response({
            "revenue_dynamic": OperatorStatisticsService.revenue_last_6_months(operator),
            "conversion_funnel": OperatorStatisticsService.conversion_funnel(operator, month_date),
            "avg_deal_value": OperatorStatisticsService.average_deal_value(operator, month_date),
            "sales_cycle": OperatorStatisticsService.sales_cycle(operator, month_date),
            "retention": OperatorStatisticsService.retention(operator, month_date),
        })
