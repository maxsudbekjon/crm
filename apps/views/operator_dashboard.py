from datetime import datetime, time
from django.utils.timezone import localtime, now
from django.db.models import Count, Q, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.models.operator import Operator
from apps.models.leads import Lead

class OperatorsDashboardAPIView(APIView):
    def get(self, request):
        # Oy boshini aniqlaymiz
        today = localtime(now()).date()
        month_start = datetime.combine(today.replace(day=1), time.min)

        # Operatorlarni olish + lead va sold_leads
        operators = Operator.objects.select_related("user").annotate(
            total_leads=Count(
                "leads",
                filter=Q(leads__created_at__gte=month_start),
                distinct=True
            ),
            sold_leads=Count(
                "leads",
                filter=Q(
                    leads__status=Lead.Status.SOLD,
                    leads__created_at__gte=month_start
                ),
                distinct=True
            )
        )

        operators_data = []
        conversions = []

        for operator in operators:
            total = operator.total_leads or 0
            sold = operator.sold_leads or 0

            conversion = round((sold / total) * 100, 2) if total else 0
            conversions.append(conversion)

            # Daromad (oy boshidan hozirgi kungacha)

            income = Lead.objects.filter(
                operator=operator,
                status=Lead.Status.SOLD,
                created_at__gte=month_start
            ).aggregate(
                total_income=Sum('course__price')
            )['total_income'] or 0

            operator_name = operator.user.get_full_name().strip()
            operators_data.append({
                "xodim": operator_name if operator_name else operator.user.username,
                "aloqa": {"email": operator.user.email or ""},
                "lavozim": operator.status or "Operator",
                "lead": total,
                "sotilgan": sold,
                "konversiya": conversion,
                "daromad": income
            })

        # Shu yerga qo‘shamiz
        oylik_leadlar = Lead.objects.filter(created_at__gte=month_start).count()

        return Response({
            "cards": {
                "oylik_leadlar": oylik_leadlar,
                "oylik_daromad": sum([op['daromad'] for op in operators_data]),
                "aktiv_operatorlar": Operator.objects.filter(user__is_active=True).count(),
                "oylik_konversiya": round(sum(conversions)/len(conversions), 2) if conversions else 0
            },
            "operator_samaradorligi": operators_data
        })
