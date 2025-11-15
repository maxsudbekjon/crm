
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q, Avg
from apps.models import Lead, Call, Task, Penalty


@api_view(['GET'])
def analytics_api(request):
    # 1️⃣ Jami leadlar soni
    total_leads = Lead.objects.count()

    # 2️⃣ Conversion rate
    sold_leads = Lead.objects.filter(status=Lead.Status.SOLD).count()
    conversion_rate = (sold_leads / total_leads * 100) if total_leads > 0 else 0

    # 3️⃣ O‘rtacha qo‘ng‘iroq davomiyligi
    avg_call_duration = Call.objects.aggregate(
        avg_duration=Avg('duration_seconds')
    )['avg_duration'] or 0

    # 4️⃣ Task completion foizi
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(completed=True).count()
    tasks_completed_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # 5️⃣ O‘rtacha jarima ballari
    avg_penalties = Penalty.objects.aggregate(
        avg_points=Avg('points')
    )['avg_points'] or 0

    data = {
        "total_leads": total_leads,
        "conversion_rate": round(conversion_rate, 2),
        "avg_call_duration": round(avg_call_duration, 2),
        "tasks_completed_percent": round(tasks_completed_percent, 2),
        "avg_penalties": round(avg_penalties, 2),
    }

    return Response(data)

