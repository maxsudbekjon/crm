from django.db.models import Sum
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.models import Operator, Lead, Task, Contract, SMS, Call, Penalty, Payment, OperatorMonthlySalary, operator
from apps.permissions import IsAdminRole
from datetime import timedelta, datetime
from rest_framework import request



# =========================
# Operator Analytics
# =========================

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






@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def analytics_api(request):

    # =========================
    # 1. Oyni aniqlash
    # =========================
    month_param = request.query_params.get("month")
    if month_param:
        month_start = parse_date(month_param + "-01")
    else:
        today = timezone.now().date()
        month_start = today.replace(day=1)

    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1)

    # =========================
    # 2. Leadlar (oy bo‘yicha)
    # =========================
    leads_qs = Lead.objects.filter(
        created_at__gte=month_start,
        created_at__lt=month_end
    ).select_related("course", "operator")

    total_leads_count = leads_qs.count()
    total_sold_leads_count = leads_qs.filter(status=Lead.Status.SOLD).count()

    total_leads_sum = sum(
        l.course.price for l in leads_qs if l.course
    )

    sold_leads_sum = sum(
        l.course.price for l in leads_qs
        if l.course and l.status == Lead.Status.SOLD
    )

    conversion = round(
        (total_sold_leads_count / total_leads_count) * 100, 1
    ) if total_leads_count else 0



    # =========================
    # 3. Operatorlar bo‘yicha
    # =========================
    operators_data = []

    operators = Operator.objects.select_related("user")
    for op in operators:
        op_leads = leads_qs.filter(operator=op)

        op_total_leads_count = op_leads.count()
        op_sold_leads_count = op_leads.filter(status=Lead.Status.SOLD).count()

        op_leads_sum = sum(
            l.course.price for l in op_leads if l.course
        )

        op_sold_sum = sum(
            l.course.price for l in op_leads
            if l.course and l.status == Lead.Status.SOLD
        )

        op_conversion = round(
            (op_sold_leads_count / op_total_leads_count) * 100, 1
        ) if op_total_leads_count else 0

        op_daromad = op.monthly_salaries.filter(
            month=month_start
        ).aggregate(total=Sum("commission"))["total"] or 0

        op_calls_count = op.calls.filter(
            call_time__gte=month_start,
            call_time__lt=month_end
        ).count()
        if op_total_leads_count > 0:
            operators_data.append({
                "operator": op.user.username,
                "total_leads": op_total_leads_count,
                "sold_leads": op_sold_leads_count,
                "op_calls_count": op_calls_count,
                "conversion": op_conversion,
                "daromad": float(op_daromad),
            })

    # =========================
    # 4. Umumiy daromad
    # =========================
    total_daromad = Payment.objects.filter(
        created_at__gte=month_start,
        created_at__lt=month_end
    ).aggregate(total=Sum("amount"))["total"] or 0

    return Response({
        "month": month_start,
        "summary": {
            "total_leads": total_leads_count,
            "total_sold_leads": total_sold_leads_count,
            "total_leads_sum": float(total_leads_sum),
            "total_daromad": float(total_daromad),
            "active_operators": len(operators_data),
            "conversion": conversion,
        },
        "operators": operators_data
    })



@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def source_conversion_api(request):

    month_param = request.query_params.get("month")

    if month_param:
        month_start = timezone.make_aware(
            datetime.strptime(month_param + "-01", "%Y-%m-%d")
        )
    else:
        today = timezone.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0)

    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1)
    qs = (
        Lead.objects
        .filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        )
        .values("source")
        .annotate(
            total=Count("id"),
            sold=Count(
                "id",
                filter=Q(status=Lead.Status.SOLD)
            )
        )
    )

    data = []
    for row in qs:
        total = row["total"]
        sold = row["sold"]
        conversion = round((sold / total) * 100, 1) if total else 0

        data.append({
            "source": row["source"],
            "total": total,
            "sold": sold,
            "conversion": conversion
        })
    print("ROLE:", request.user.role)
    print("IS_STAFF:", request.user.is_staff)
    print("IS_SUPERUSER:", request.user.is_superuser)
    return Response({
        "sources": data,
    })



@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def weekly_dynamics_api(request):
    today = timezone.now().date()
    # Haftaning boshlanishini aniqlash (0 = bugungi kun)
    start_date = today - timedelta(days=28)  # oxirgi 4 hafta

    data = []
    for i in range(4):
        week_start = start_date + timedelta(weeks=i)
        week_end = week_start + timedelta(weeks=1)

        leads_count = Lead.objects.filter(
            created_at__gte=week_start,
            created_at__lt=week_end
        ).count()

        sold_count = Lead.objects.filter(
            created_at__gte=week_start,
            created_at__lt=week_end,
            status=Lead.Status.SOLD
        ).count()

        data.append({
            "week": f"{i+1}-hafta",
            "leads": leads_count,
            "sold": sold_count
        })

    return Response({
        "weekly_dynamics": data
    })