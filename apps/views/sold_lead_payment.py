from django.db.models import Sum
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Lead


class SoldClientsPaymentsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Response(
            description="Payment results",
            examples={"application/json": [{"lead_id": 1, "total_payment": 500000}]}
        )}
    )
    def get(self, request):
        sold_leads = Lead.objects.filter(status='sold')
        results = []

        for lead in sold_leads:
            total_payment = lead.payment_set.aggregate(total=Sum('amount'))['total'] or 0
            operator = lead.operator
            operator_bonus = operator.salary * 0.1 if operator and hasattr(operator, 'salary') else 0

            results.append({
                'lead_id': lead.id,
                'lead_name': lead.full_name,
                'total_payment': total_payment,
                'operator_id': operator.id if operator else None,
                'operator_name': operator.user.full_name if operator else None,
                'operator_bonus': operator_bonus
            })
        return Response(results, status=status.HTTP_200_OK)

