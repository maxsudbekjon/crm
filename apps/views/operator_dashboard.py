from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.models.operator import Operator
from apps.models.leads import Lead


class OperatorsDashboardAPIView(APIView):
    def get(self, request):
        operators = Operator.objects.select_related("user").annotate(
            total_leads=Count("leads", distinct=True),
            sold_leads=Count(
                "leads",
                filter=Q(leads__status=Lead.Status.SOLD),
                distinct=True
            )
        )

        operators_data = []
        conversions = []

        for operator in operators:
            total = operator.total_leads or 0
            sold = operator.sold_leads or 0

            # Konversiya (0 ga bo‘lishdan himoya)
            conversion = round((sold / total) * 100, 2) if total else 0
            conversions.append(conversion)

            # Daromad (Decimal → float xavfsiz)
            income = round(sold * float(operator.salary or 0), 2)

            operators_data.append({
                # Agar full_name bo‘sh bo‘lsa — username chiqadi
                "xodim": (
                    operator.user.get_full_name().strip()
                    if operator.user.get_full_name().strip()
                    else operator.user.username
                ),
                "aloqa": {
                    "email": operator.user.email or ""
                },
                # status bo‘sh bo‘lsa fallback
                "lavozim": operator.status or "Operator",
                "lead": total,
                "sotilgan": sold,
                "konversiya": conversion,
                "daromad": income
            })

        return Response({
            "cards": {
                "jami_operatorlar": Operator.objects.count(),
                "aktiv_operatorlar": Operator.objects.count(),  # is_active yo‘q
                "jami_sotilgan": Lead.objects.filter(
                    status=Lead.Status.SOLD
                ).count(),
                "ortacha_konversiya": round(
                    sum(conversions) / len(conversions), 2
                ) if conversions else 0
            },
            "operators": operators_data
        })
