import datetime

from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.models import Operator, Lead, Task, Contract, SMS, Call, Penalty




@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('operator_id', openapi.IN_QUERY, description="Analitika olish uchun operator ID", type=openapi.TYPE_INTEGER, required=True)
    ],
    operation_description="Bitta operator uchun kunlik va oylik analitika (calls, messages va o‘qiyotganlar bilan birga)",
    responses={200: openapi.Response(description="Operator analitika natijasi")}
)
@api_view(['GET'])
def operator_analytics(request):
    operator_id = request.GET.get('operator_id')
    if not operator_id:
        return JsonResponse({"error": "operator_id parametri kerak"}, status=400)

    try:
        operator = Operator.objects.get(id=operator_id)
    except Operator.DoesNotExist:
        return JsonResponse({"error": "Operator topilmadi"}, status=404)

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Leadlar
    today_leads = Lead.objects.filter(operator=operator, created_at__date=today).count()
    month_leads = Lead.objects.filter(operator=operator, created_at__date__gte=month_start).count()
    today_sold_leads = Lead.objects.filter(operator=operator, status="sold", created_at__date=today).count()
    month_sold_leads = Lead.objects.filter(operator=operator, status="sold", created_at__date__gte=month_start).count()

    conversion_rate_today = round((today_sold_leads / today_leads) * 100, 2) if today_leads else 0
    conversion_rate_month = round((month_sold_leads / month_leads) * 100, 2) if month_leads else 0

    # Tasklar
    start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))

    today_tasks_done = Task.objects.filter(operator=operator, is_completed=True, completed_at__gte=start, completed_at__lte=end).count()
    today_tasks_pending = Task.objects.filter(operator=operator, is_completed=False, deadline__gte=timezone.now()).count()
    today_tasks_overdue = Task.objects.filter(operator=operator, is_completed=False, deadline__lt=timezone.now()).count()
    month_tasks_done = Task.objects.filter(operator=operator, is_completed=True, completed_at__date__gte=month_start).count()

    # Daromad
    today_income = float(Contract.objects.filter(operator=operator, created_at__date=today).aggregate(total=Sum("amount_paid"))["total"] or 0) * 0.1
    month_income = float(Contract.objects.filter(operator=operator, created_at__date__gte=month_start).aggregate(total=Sum("amount_paid"))["total"] or 0) * 0.1

    # Calls va Messages
    today_calls = Call.objects.filter(operator=operator, created_at__date=today).count()
    today_messages = SMS.objects.filter(operator=operator, sent_at__date=today).count()
    today_call_seconds = Call.objects.filter(operator=operator, created_at__date=today).aggregate(total=Sum("duration_seconds"))["total"] or 0
    minutes = today_call_seconds // 60
    seconds = today_call_seconds % 60
    today_call_duration = f"{minutes} min {seconds} sec"

    # Jarimalar
    today_penalties = Penalty.objects.filter(operator=operator, created_at__date=today).aggregate(total_points=Sum("points"))["total_points"] or 0
    month_penalties = Penalty.objects.filter(operator=operator, created_at__date__gte=month_start).aggregate(total_points=Sum("points"))["total_points"] or 0

    result = {
        "operator": operator.user.full_name,
        "branch": operator.branch.name,
        "daily": {
            "today_leads": today_leads,
            "today_sold_leads": today_sold_leads,
            "calls": today_calls,
            "today_call_duration": today_call_duration,
            "messages": today_messages,
            "today_tasks_done": today_tasks_done,
            "today_tasks_pending": today_tasks_pending,
            "today_tasks_overdue": today_tasks_overdue,
            "today_income": today_income,
            "today_penalties": today_penalties,
            "conversion_rate_today": conversion_rate_today,
        },
        "monthly": {
            "month_leads": month_leads,
            "month_sold_leads": month_sold_leads,
            "month_income": month_income,
            "month_tasks_done": month_tasks_done,
            "month_penalties": month_penalties,
            "conversion_rate_month": conversion_rate_month,
        },
    }

    return JsonResponse(result, safe=False)


@api_view(['GET'])
def analytics_api(request):
    now = timezone.now()

    week_sold = Lead.objects.filter(
        status=Lead.Status.SOLD,
        updated_at__gte=now - timedelta(days=7)
    ).count()

    month_sold = Lead.objects.filter(
        status=Lead.Status.SOLD,
        updated_at__gte=now - timedelta(days=30)
    ).count()

    top_operator_leads = (
        Operator.objects.annotate(lead_count=Count('leads'))
        .order_by('-lead_count')
        .values('user__username', 'lead_count')
        .first()
    )

    top_operator_sales = (
        Operator.objects.annotate(
            sold_count=Count('leads', filter=Q(leads__status=Lead.Status.SOLD))
        )
        .order_by('-sold_count')
        .values('user__username', 'sold_count')
        .first()
    )

    overall_leads = Lead.objects.all().count()
    sold_leads = Lead.objects.filter(status=Lead.Status.SOLD).count()

    week_created = Lead.objects.filter(
        created_at__gte=now - timedelta(days=7)
    ).count()

    month_created = Lead.objects.filter(
        created_at__gte=now - datetime.timedelta(days=30)
    ).count()

    data = {
        "sold_last_week": week_sold,
        "sold_last_month": month_sold,
        "top_operator_by_leads": top_operator_leads,
        "top_operator_by_sales": top_operator_sales,
        "lead_created_last_week": week_created,
        "lead_created_last_month": month_created,
        "overall_leads": overall_leads,
        "sold_leads": sold_leads
    }

    return Response(data)