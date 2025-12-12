from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count
from apps.models.leads import Lead
from apps.models.operator import Operator
from apps.models.call import Call


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        operator = Operator.objects.filter(user=user).first()
        if not operator:
            return Response({"error": "Operator not found for this user."}, status=400)

        today = timezone.now().date()

        # -----------------------------------------------
        # TODAY METRICS ONLY
        # -----------------------------------------------

        # 1. Today leads
        today_leads = Lead.objects.filter(
            operator=operator,
            created_at__date=today
        ).count()

        # 2. Today calls
        today_calls = Call.objects.filter(
            operator=operator,
            created_at__date=today
        ).count()

        # 3. Today sold leads
        today_sold_leads = Lead.objects.filter(
            operator=operator,
            status='sold',
            updated_at__date=today
        ).count()

        # 4. Today conversion (sold_today / leads_today)
        conversion_rate = (
            round((today_sold_leads / today_leads) * 100, 2)
            if today_leads > 0 else 0
        )

        # ---------------------------------------------------------
        # WEEKLY STATUS (MONDAY → SATURDAY)
        # ---------------------------------------------------------
        weekday_index = today.weekday()  # 0 = Monday
        monday = today - timezone.timedelta(days=weekday_index)

        week_data = []
        for i in range(6):  # Monday → Saturday
            day = monday + timezone.timedelta(days=i)

            leads_count = Lead.objects.filter(
                operator=operator,
                created_at__date=day
            ).count()

            calls_count = Call.objects.filter(
                operator=operator,
                created_at__date=day
            ).count()

            week_data.append({
                "day": day.strftime("%a"),
                "leads": leads_count,
                "calls": calls_count
            })

        return Response({
            "today_leads": today_leads,
            "today_calls": today_calls,
            "today_sold": today_sold_leads,
            "conversion_rate": conversion_rate,
            "weekly_status": week_data
        })
