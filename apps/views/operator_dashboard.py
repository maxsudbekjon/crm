from datetime import datetime, time
from django.utils import timezone
from django.db.models import Count, Q, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.models.operator import Operator
from apps.models.leads import Lead
from apps.serializers.operator_status import OperatorDataSerializer


class OperatorsDashboardAPIView(APIView):

    def get(self, request):

        # Oy boshini aniqlaymiz
        today = timezone.localdate()
        month_start = timezone.make_aware(datetime.combine(today.replace(day=1), time.min))

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
        total_leads_month = 0
        total_sold_month = 0

        for operator in operators:
            total = operator.total_leads or 0
            sold = operator.sold_leads or 0

            total_leads_month += total
            total_sold_month += sold

            conversion = round((sold / total) * 100, 2) if total else 0

            # Daromad (oy boshidan hozirgi kungacha)
            income = Lead.objects.filter(
                operator=operator,
                status=Lead.Status.SOLD,
                created_at__gte=month_start
            ).aggregate(total_income=Sum('course__price'))['total_income'] or 0

            # Xodimning ismi va ish boshlash sanasi
            operator_name = operator.user.get_full_name().strip() if operator.user.get_full_name() else operator.user.username
            start_working = operator.start_date.strftime("%d-%m-%Y") if getattr(operator, 'start_date', None) else "Noma'lum"

            operators_data.append({
                "xodim": operator_name,
                "ish_boshlangan": start_working,
                "lavozim": operator.status or "Operator",
                "lead": total,
                "sotilgan": sold,
                "konversiya": conversion,
                "daromad": income
            })

        # Oylik jami leadlar va daromad
        oylik_leadlar = total_leads_month
        oylik_daromad = sum(op['daromad'] for op in operators_data)
        oylik_konversiya = round((total_sold_month / total_leads_month) * 100, 2) if total_leads_month else 0

        return Response({
            "cards": {
                "oylik_leadlar": oylik_leadlar,
                "oylik_daromad": oylik_daromad,
                "aktiv_operatorlar": Operator.objects.filter(user__is_active=True).count(),
                "oylik_konversiya": oylik_konversiya
            },
            "operator_samaradorligi": OperatorDataSerializer(operators_data, many=True).data
        })
