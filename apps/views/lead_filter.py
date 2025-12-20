from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

from apps.models.leads import Lead
from apps.serializers.lead_serializers import LeadSerializer


class LeadFilterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    SECTION_STATUS = {
        "need_contact": "Bog‘lanish kerak",
        "info_provided": "Ma’lumot berildi",
        "meeting_scheduled": "Uchrashuv belgilandi",
        "sold": "Uchrashuv o‘tkazildi",
    }

    def filter_by_period(self, queryset, period):
        if not period:
            return queryset

        today = timezone.now().date()

        if period == "bugun":
            return queryset.filter(created_at__date=today)

        if period == "kecha":
            return queryset.filter(created_at__date=today - timedelta(days=1))

        if period == "3_kun_oldin":
            return queryset.filter(created_at__date__gte=today - timedelta(days=3))

        if period == "1_hafta_oldin":
            return queryset.filter(created_at__date__gte=today - timedelta(days=7))

        if period == "1_oy_oldin":
            return queryset.filter(created_at__date__gte=today - timedelta(days=30))

        return queryset

    # 🔹 TEPADAGI 4 TA UCHUN (COUNT + SUM, FILTERSIZ)
    def section_data(self, queryset, key):
        leads_qs = queryset.filter(status=key)
        return {
            "name": self.SECTION_STATUS[key],
            "count": leads_qs.count(),
            "sum": leads_qs.aggregate(
                total=Sum("payments__amount")
            )["total"] or 0
        }

    def get(self, request, period=None, *args, **kwargs):
        period_from_query = request.query_params.get("period")
        period = period or period_from_query  # ❗ default yo‘q

        section = request.query_params.get("section")

        # ===============================
        # 1️⃣ TEPADAGI 4 TA (FILTERSIZ)
        # ===============================
        all_leads_qs = Lead.objects.all()

        sections = {
            key: self.section_data(all_leads_qs, key)
            for key in self.SECTION_STATUS
        }

        # ===============================
        # 2️⃣ 7-FRAME (FILTER BILAN)
        # ===============================
        leads_qs = Lead.objects.all()

        if period:
            leads_qs = self.filter_by_period(leads_qs, period)

        if section:
            if section not in self.SECTION_STATUS:
                return Response({"detail": "Noto'g'ri section"}, status=400)
            leads_qs = leads_qs.filter(status=section)

        leads_data = LeadSerializer(leads_qs, many=True).data

        return Response({
            "period": period,
            "sections": sections,  # 🔥 doim to‘liq (count + sum)
            "leads": leads_data    # 🔥 filter faqat shu yerda
        })