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
        today = timezone.now().date()
        if period == "bugun":
            return queryset.filter(created_at__date=today)
        elif period == "kecha":
            return queryset.filter(created_at__date=today - timedelta(days=1))
        else:
            return queryset  # boshqa filter bo‘lmasa hamma leads

    def section_data(self, queryset, key):
        leads_qs = queryset.filter(status=key)
        return {
            "name": self.SECTION_STATUS[key],
            "count": leads_qs.count(),
            "sum": leads_qs.aggregate(total=Sum("payments__amount"))["total"] or 0
        }

    def get(self, request, *args, **kwargs):
        period = request.query_params.get("period")  # bugun yoki kecha
        section = request.query_params.get("section")

        # Sections (filtersiz)
        all_leads_qs = Lead.objects.all()
        sections = {key: self.section_data(all_leads_qs, key) for key in self.SECTION_STATUS}

        # Leads filter bilan
        leads_qs = Lead.objects.all()
        if period in ["bugun", "kecha"]:
            leads_qs = self.filter_by_period(leads_qs, period)

        if section:
            if section not in self.SECTION_STATUS:
                return Response({"detail": "Noto'g'ri section"}, status=400)
            leads_qs = leads_qs.filter(status=section)

        leads_data = LeadSerializer(leads_qs, many=True).data  # faqat id, full_name, phone

        return Response({
            "period": period,
            "sections": sections,
            "leads": leads_data
        })