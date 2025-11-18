from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q
from apps.models import Lead, Operator


@api_view(['GET'])
def analytics_api(request):
    now = timezone.now()

    # 1 hafta va 1 oy ichida sotilgan leadlar
    week_sold = Lead.objects.filter(
        status=Lead.Status.SOLD,
        updated_at__gte=now - timedelta(days=7)
    ).count()

    month_sold = Lead.objects.filter(
        status=Lead.Status.SOLD,
        updated_at__gte=now - timedelta(days=30)
    ).count()

    # Eng ko'p lead olgan operator
    top_operator_leads = (
        Operator.objects.annotate(lead_count=Count('leads'))
        .order_by('-lead_count')
        .values('full_name', 'lead_count')
        .first()
    )

    # Eng yaxshi sotgan operator
    top_operator_sales = (
        Operator.objects.annotate(
            sold_count=Count('leads', filter=Q(leads__status=Lead.Status.SOLD))
        )
        .order_by('-sold_count')
        .values('full_name', 'sold_count')
        .first()
    )

    overall_leads = Lead.objects.all().count()
    sold_leads = Lead.objects.filter(status=Lead.Status.SOLD).count()

    # Oxirgi 1 hafta va 1 oy ichida kelgan leadlar soni
    week_created = Lead.objects.filter(
        created_at__gte=now - timedelta(days=7)
    ).count()

    month_created = Lead.objects.filter(
        created_at__gte=now - timedelta(days=30)
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
