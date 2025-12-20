from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Count, Avg, Sum, Q
from apps.models.leads import Lead
from apps.models.operator import Operator
from apps.utils import first_day_of_month, month_range
from django.db.models import Count, Case, When, IntegerField, F, FloatField, ExpressionWrapper
from django.utils.timezone import now

class DirectorStatisticsService:
    """
    Aggregated statistics across ALL operators
    """

    # -------------------------------
    # Revenue dynamics (last 6 months)
    # -------------------------------
    @staticmethod
    def revenue_last_6_months():
        today = date.today()
        months = [(today.replace(day=1) - timedelta(days=30 * i)) for i in range(5, -1, -1)]
        results = []

        for month_date in months:
            start, end = month_range(month_date)

            total_leads_price = (
                Lead.objects.filter(
                    created_at__range=[start, end],
                    course__isnull=False
                )
                .aggregate(total=Sum("course__price"))["total"] or Decimal("0")
            )

            sold_leads_price = (
                Lead.objects.filter(
                    created_at__range=[start, end],
                    status=Lead.Status.SOLD,
                    course__isnull=False
                )
                .aggregate(total=Sum("course__price"))["total"] or Decimal("0")
            )

            results.append({
                "month": month_date.strftime("%b"),
                "total_revenue": float(total_leads_price),
                "sold_revenue": float(sold_leads_price),
            })

        return results

    @staticmethod
    def get_period_range(period: str):
        today = date.today()

        if period == "today":
            start = today
            end = today + timedelta(days=1)

        elif period == "week":
            start = today - timedelta(days=today.weekday())  # Monday
            end = start + timedelta(days=7)

        else:  # month (default)
            start, end = month_range(today)

        return start, end

    @staticmethod
    def sellers_performance(period: str = "month"):
        start, end = DirectorStatisticsService.get_period_range(period)

        qs = (
            Operator.objects
            .annotate(
                total_leads=Count(
                    "leads",
                    filter=Q(leads__created_at__range=[start, end])
                ),
                sold_leads=Count(
                    "leads",
                    filter=Q(
                        leads__created_at__range=[start, end],
                        leads__status=Lead.Status.SOLD
                    )
                ),
            )
            .annotate(
                conversion_rate=Case(
                    When(
                        total_leads__gt=0,
                        then=ExpressionWrapper(
                            F("sold_leads") * 100.0 / F("total_leads"),
                            output_field=FloatField()
                        )
                    ),
                    default=0.0,
                    output_field=FloatField()
                )
            )
            .filter(total_leads__gt=0)
            .order_by("-conversion_rate")
        )

        return [
            {
                "operator": operator.user.username,
                "conversion_rate": round(operator.conversion_rate, 1),
                "sold_leads": operator.sold_leads,
                "total_leads": operator.total_leads,
            }
            for operator in qs
        ]

    @staticmethod
    def conversion_funnel(period: str = "month"):
        start, end = DirectorStatisticsService.get_period_range(period)
        qs = Lead.objects.filter(created_at__range=[start, end])

        return {
            "lead": qs.count(),
            "aloqa": qs.filter(last_contact_date__isnull=False).count(),
            "taklif": qs.filter(status=Lead.Status.INFO_PROVIDED).count(),
            "muzokara": qs.filter(status=Lead.Status.MEETING_SCHEDULED).count(),
            "yopilgan": qs.filter(status=Lead.Status.SOLD).count(),
        }

    @staticmethod
    def average_deal_value(month_date: date):
        start, end = month_range(month_date)

        current_avg = (
            Lead.objects.filter(
                status=Lead.Status.SOLD,
                created_at__range=[start, end],
                course__isnull=False
            )
            .aggregate(avg=Avg("course__price"))["avg"] or Decimal("0")
        )

        prev_month = (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        ps, pe = month_range(prev_month)

        prev_avg = (
            Lead.objects.filter(
                status=Lead.Status.SOLD,
                created_at__range=[ps, pe],
                course__isnull=False
            )
            .aggregate(avg=Avg("course__price"))["avg"] or Decimal("0")
        )

        if prev_avg == 0:
            delta = 100
        else:
            delta = ((current_avg - prev_avg) / prev_avg) * 100

        return {
            "value": round(float(current_avg), 1),
            "delta": round(float(delta), 1)
        }

    @staticmethod
    def sales_cycle(month_date: date):
        start, end = month_range(month_date)

        sold = Lead.objects.filter(
            status=Lead.Status.SOLD,
            created_at__range=[start, end]
        )

        if not sold.exists():
            return {"days": 0, "delta": 0}

        days = (sold.latest("created_at").created_at.date() -
                sold.earliest("created_at").created_at.date()).days

        prev_month = (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        ps, pe = month_range(prev_month)

        prev_sold = Lead.objects.filter(
            status=Lead.Status.SOLD,
            created_at__range=[ps, pe]
        )

        prev_days = 0
        if prev_sold.exists():
            prev_days = (prev_sold.latest("created_at").created_at.date() -
                         prev_sold.earliest("created_at").created_at.date()).days

        return {
            "days": days,
            "delta": prev_days - days
        }

    @staticmethod
    def retention(month_date: date):
        start, end = month_range(month_date)

        total = Lead.objects.filter(created_at__range=[start, end]).count()
        sold = Lead.objects.filter(
            created_at__range=[start, end],
            status=Lead.Status.SOLD
        ).count()

        current_rate = (sold / total * 100) if total > 0 else 0

        prev_month = (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        ps, pe = month_range(prev_month)

        prev_total = Lead.objects.filter(created_at__range=[ps, pe]).count()
        prev_sold = Lead.objects.filter(
            created_at__range=[ps, pe],
            status=Lead.Status.SOLD
        ).count()

        prev_rate = (prev_sold / prev_total * 100) if prev_total > 0 else 0

        delta = 100 if prev_rate == 0 else current_rate - prev_rate

        return {
            "rate": round(current_rate, 1),
            "delta": round(delta, 1)
        }

