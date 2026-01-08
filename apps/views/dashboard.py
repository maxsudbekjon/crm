from django.db.models import Count, Q, Sum
from django.utils.timezone import now, localtime
from rest_framework.views import APIView
from rest_framework.response import Response
from dateutil.relativedelta import relativedelta
from apps.models.leads import Lead
from apps.models.operator import Operator

class DashboardMonthlyAPIView(APIView):
    def get(self, request):
        today = localtime(now()).date()
        current_year = today.year
        current_month = today.month


        monthly_leads = Lead.objects.filter(
            created_at__year=current_year,
            created_at__month=current_month
        ).count()

        monthly_sold = Lead.objects.filter(
            status=Lead.Status.SOLD,
            created_at__year=current_year,
            created_at__month=current_month
        )

        monthly_revenue = (
            Lead.objects
            .filter(
                created_at__year=current_year,
                created_at__month=current_month,
                status=Lead.Status.SOLD,
                course__isnull=False
            )
            .aggregate(total=Sum("course__price"))["total"] or 0
        )

        active_operators = Operator.objects.filter(
            leads__created_at__year=current_year,
            leads__created_at__month=current_month
        ).distinct().count()

        conversion = (
            round((monthly_sold.count() / monthly_leads) * 100, 2)
            if monthly_leads else 0
        )


        operators = Operator.objects.select_related("user").annotate(
            total_leads=Count(
                "leads",
                filter=Q(
                    leads__created_at__year=current_year,
                    leads__created_at__month=current_month
                )
            ),
            sold_leads=Count(
                "leads",
                filter=Q(
                    leads__status=Lead.Status.SOLD,
                    leads__created_at__year=current_year,
                    leads__created_at__month=current_month
                )
            )
        ).order_by('-sold_leads')[:5]

        operator_chart = []
        for op in operators:
            full_name = op.user.get_full_name().strip()
            operator_chart.append({
                "operator": full_name if full_name else op.user.username,
                "leadlar": op.total_leads,
                "sotilganlar": op.sold_leads
            })


        six_months_ago = today - relativedelta(months=6)
        revenue_last_6_months = []

        for i in range(6):
            month_date = today - relativedelta(months=i)
            month_revenue = (
                Lead.objects
                .filter(
                    status=Lead.Status.SOLD,
                    created_at__year=month_date.year,
                    created_at__month=month_date.month,
                    course__isnull=False
                )
                .aggregate(total=Sum("course__price"))["total"] or 0
            )
            revenue_last_6_months.append({
                "year": month_date.year,
                "month": month_date.month,
                "daromad": round(month_revenue, 2)
            })

        return Response({
            "cards": {
                "oylik_leadlar": monthly_leads,
                "oylik_daromad": round(monthly_revenue, 2),
                "aktiv_operatorlar": active_operators,
                "oylik_konversiya": conversion
            },
            "operator_samaradorligi": operator_chart,
            "oy6_daromad": revenue_last_6_months
        })
