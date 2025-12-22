from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

from apps.models.leads import Lead
from apps.models.operator import Operator
from apps.serializers.lead_serializers import LeadSerializer


SECTION_STATUS = {
    "need_contact": "Bog‘lanish kerak",
    "info_provided": "Ma’lumot berildi",
    "meeting_scheduled": "Uchrashuv belgilandi",
    "sold": "Uchrashuv o‘tkazildi",
}


class LeadFilterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def filter_by_period(self, queryset, period):
        today = timezone.now().date()

        if period == "bugun":
            return queryset.filter(created_at__date=today)
        elif period == "kecha":
            return queryset.filter(created_at__date=today - timedelta(days=1))
        elif period == "3kun_oldin":
            start_date = today - timedelta(days=3)
            return queryset.filter(created_at__date__gte=start_date)
        elif period == "1xafta_oldin":
            start_date = today - timedelta(days=7)
            return queryset.filter(created_at__date__gte=start_date)
        elif period == "1oy_oldin":
            start_date = today - timedelta(days=30)
            return queryset.filter(created_at__date__gte=start_date)
        return queryset  # default: barchasi

    def section_data(self, queryset, key):
        leads_qs = queryset.filter(status=key)
        return {
            "name": SECTION_STATUS[key],
            "count": leads_qs.count(),
            "sum": leads_qs.aggregate(total=Sum("payments__amount"))["total"] or 0
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="section",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Filter by section",
                required=False,
                enum=[str(k) for k in SECTION_STATUS.keys()]
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Query param orqali faqat section tanlanadi:
        /leads/filter/?section=need_contact
        Period backendda default: barchasi
        """
        period = "barchasi"  # default
        section = request.query_params.get("section")
        user = request.user

        # Operator faqat o'z leadlarini ko'radi
        if user.is_staff:
            leads_qs = Lead.objects.all()
        else:
            try:
                leads_qs = Lead.objects.filter(operator=user.operator)
            except Operator.DoesNotExist:
                return Response({"detail": "Siz operator emassiz"}, status=403)

        # Sectionlar statistikasi
        sections = {key: self.section_data(leads_qs, key) for key in SECTION_STATUS}

        # Period filter
        leads_qs = self.filter_by_period(leads_qs, period)

        # Section filter
        if section:
            if section not in SECTION_STATUS:
                return Response({"detail": "Noto'g'ri section"}, status=400)
            leads_qs = leads_qs.filter(status=section)

        leads_data = LeadSerializer(leads_qs, many=True).data

        return Response({
            "period": period,
            "sections": sections,
            "leads": leads_data
        })
