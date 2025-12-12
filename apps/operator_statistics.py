from datetime import date, timedelta
from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncMonth
from leads.models import Lead
from operator_salary.models import OperatorMonthlySalary
from apps.utils.date_utils import first_day_of_month, month_range


class OperatorStatisticsService:

    @staticmethod
    def revenue_last_6_months(operator):
        today = date.today()
        last_6 = [(today.replace(day=1) - timedelta(days=30 * i)) for i in range(5, -1, -1)]
        results = []

        for month_date in last_6:
            start, end = month_range(month_date)

            sold_leads_sum = Lead.objects.filter(
                operator=operator,
                status=Lead.Status.SOLD,
                created_at__range=[start, end]
            ).count() * 1  # each sold lead = 1 price? (you said no price field)

            salary = OperatorMonthlySalary.objects.filter(
                operator=operator,
                month=first_day_of_month(month_date)
            ).first()

            month_salary = salary.total_salary if salary else 0

            results.append({
                "month": month_date.strftime("%b"),
                "revenue": sold_leads_sum,
                "profit": month_salary,
            })

        return results

    @staticmethod
    def conversion_funnel(operator, month_date: date):
        start, end = month_range(month_date)

        qs = Lead.objects.filter(operator=operator, created_at__range=[start, end])

        return {
            "lead": qs.count(),
            "aloqa": qs.filter(last_contact_date__isnull=False).count(),
            "taklif": qs.filter(status=Lead.Status.INFO_PROVIDED).count(),
            "muzokara": qs.filter(status=Lead.Status.MEETING_SCHEDULED).count(),
            "yopilgan": qs.filter(status=Lead.Status.SOLD).count(),
        }

    @staticmethod
    def average_deal_value(operator, month_date: date):
        start, end = month_range(month_date)
        current = Lead.objects.filter(
            operator=operator,
            status=Lead.Status.SOLD,
            created_at__range=[start, end]
        ).count()

        prev_month = (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        ps, pe = month_range(prev_month)
        previous = Lead.objects.filter(
            operator=operator,
            status=Lead.Status.SOLD,
            created_at__range=[ps, pe]
        ).count()

        delta = 0
        if previous > 0:
            delta = ((current - previous) / previous) * 100

        return {
            "value": current,
            "delta": round(delta, 1)
        }

    @staticmethod
    def sales_cycle(operator, month_date: date):
        start, end = month_range(month_date)

        sold_leads = Lead.objects.filter(
            operator=operator,
            status=Lead.Status.SOLD,
            created_at__range=[start, end]
        )

        if not sold_leads.exists():
            return {"days": 0, "delta": 0}

        days_active = (sold_leads.latest("created_at").created_at.date() -
                       sold_leads.earliest("created_at").created_at.date()).days

        # previous month
        prev_month = (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        ps, pe = month_range(prev_month)
        prev_sold = Lead.objects.filter(
            operator=operator,
            status=Lead.Status.SOLD,
            created_at__range=[ps, pe]
        )

        prev_days = 0
        if prev_sold.exists():
            prev_days = (prev_sold.latest("created_at").created_at.date() -
                         prev_sold.earliest("created_at").created_at.date()).days

        delta = prev_days - days_active

        return {"days": days_active, "delta": delta}

    @staticmethod
    def retention(operator, month_date: date):
        start, end = month_range(month_date)

        total = Lead.objects.filter(operator=operator, created_at__range=[start, end]).count()
        sold = Lead.objects.filter(operator=operator, status=Lead.Status.SOLD,
                                   created_at__range=[start, end]).count()

        current_rate = (sold / total * 100) if total > 0 else 0

        # previous month
        prev_month = (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        ps, pe = month_range(prev_month)

        prev_total = Lead.objects.filter(operator=operator, created_at__range=[ps, pe]).count()
        prev_sold = Lead.objects.filter(operator=operator, status=Lead.Status.SOLD,
                                        created_at__range=[ps, pe]).count()

        prev_rate = (prev_sold / prev_total * 100) if prev_total > 0 else 0

        delta = current_rate - prev_rate

        return {
            "rate": round(current_rate, 1),
            "delta": round(delta, 1)
        }
