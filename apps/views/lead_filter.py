from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

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

    def section_data(self, queryset, key):
        leads_qs = queryset.filter(status=key)
        return {
            "name": self.SECTION_STATUS[key],
            "count": leads_qs.count(),
            "leads": LeadSerializer(leads_qs, many=True).data
        }

    # <-- diqqat: period va boshqa URL kwargslarni qabul qilish uchun period=None, *args, **kwargs qo'shdim
    def get(self, request, period=None, *args, **kwargs):
        # 1) Avval URL orqali kelgan periodni olamiz, bo'lmasa query paramga qaraymiz
        period_from_query = request.query_params.get("period")
        period = period or period_from_query or "bugun"

        section = request.query_params.get("section")

        queryset = Lead.objects.all()
        queryset = self.filter_by_period(queryset, period)

        if section:
            if section not in self.SECTION_STATUS:
                return Response({"detail": "Noto'g'ri section"}, status=400)

            return Response({
                "period": period,
                "section": self.section_data(queryset, section)
            })

        data = {
            key: self.section_data(queryset, key)
            for key in self.SECTION_STATUS
        }

        return Response({
            "period": period,
            "sections": data
        })
