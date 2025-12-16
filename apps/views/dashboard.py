from django.db.models import Count, Q, Sum
from django.utils.timezone import now, localtime
from rest_framework.views import APIView
from rest_framework.response import Response
from dateutil.relativedelta import relativedelta

from apps.models import Course
from apps.models.leads import Lead
from apps.models.operator import Operator


class DashboardAPIView(APIView):
    def get(self, request):

        today = localtime(now()).date()  # bugungi kun lokal vaqt bo‘yicha

        # ======================
        # 1️⃣ CARDS (BUGUN)
        # ======================
        jami_leadlar = Lead.objects.filter(
            created_at__date=today
        ).count()

        jami_sotilgan = Lead.objects.filter(
            status=Lead.Status.SOLD,
            created_at__date=today
        )

        # BUGUNGI KUN DAROMADI (kurs narxlari bo‘yicha)
        bugungi_daromad = (
                Lead.objects
                .filter(
                    created_at__date=today,
                    course__isnull=False
                )
                .aggregate(total=Sum("course__price"))["total"] or 0
        )

        aktiv_operatorlar = Operator.objects.count()

        konversiya = (
            round((jami_sotilgan.count() / jami_leadlar) * 100, 2)
            if jami_leadlar else 0
        )

        # ======================
        # 2️⃣ OPERATOR SAMARADORLIGI (BUGUN)
        # ======================
        operators = Operator.objects.select_related("user").annotate(
            total_leads=Count(
                "leads",
                filter=Q(leads__created_at__date=today)
            ),
            sold_leads=Count(
                "leads",
                filter=Q(
                    leads__status=Lead.Status.SOLD,
                    leads__created_at__date=today
                )
            )
        )

        operator_chart = []
        for op in operators:
            full_name = op.user.get_full_name().strip()
            operator_chart.append({
                "operator": full_name if full_name else op.user.username,
                "leadlar": op.total_leads,
                "sotilganlar": op.sold_leads
            })

        # ======================
        # 3️⃣ OXIRGI 6 OYLIK DAROMAD
        # ======================
        six_months_ago = now() - relativedelta(months=6)

        oy6_daromad = (
            Lead.objects
            .filter(
                status=Lead.Status.SOLD,
                created_at__gte=six_months_ago,
                course__isnull=False
            )
            .aggregate(total=Sum("course__price"))["total"] or 0
        )

        return Response({
            "cards": {
                "bugungi_leadlar": jami_leadlar,
                "bugungi_daromad": round(bugungi_daromad, 2),
                "aktiv_operatorlar": aktiv_operatorlar,
                "bugungi_konversiya": konversiya
            },
            "operator_samaradorligi": operator_chart,
            "oy6_daromad": round(oy6_daromad, 2)
        })
