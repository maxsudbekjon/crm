from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.models import Lead

class DirectorStatistics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 🔐 ROLE TEKSHIRISH (TO‘G‘RI USUL)
        if request.user.role != "admin":
            return Response(
                {"detail": "Sizda bu sahifani ko‘rish huquqi yo‘q"},
                status=403
            )

        leads = Lead.objects.select_related("course", "operator")

        status_map = {
            Lead.Status.NEED_CONTACT: "boglanish_kerak",
            Lead.Status.INFO_PROVIDED: "malumot_berildi",
            Lead.Status.MEETING_SCHEDULED: "uchrashuv_belgilandi",
            Lead.Status.MEETING_CANCELLED: "uchrashuv_otkazildi",
            Lead.Status.COULD_NOT_CONTACT: "boglana_olmadik",
            Lead.Status.SOLD: "sotildi",
            Lead.Status.NOT_SOLD: "sotilmadi",
        }

        summary = {}

        for status, key in status_map.items():
            qs = leads.filter(status=status)
            summary[key] = {
                "count": qs.count(),
                "amount": qs.aggregate(
                    total=Sum("course__price")
                )["total"] or 0
            }

        lead_list = []
        for lead in leads:
            lead_list.append({
                "id": lead.id,
                "full_name": lead.full_name,
                "source": lead.source,
                "phone": lead.phone,
                "course": {
                    "name": lead.course.title if lead.course else None,
                    "price": lead.course.price if lead.course else 0,
                },
                "status": lead.status,
                "operator": lead.operator.user.full_name if lead.operator else None,
                "created_at": lead.created_at.date()
            })

        return Response({
            "summary": summary,
            "leads": lead_list
        })
