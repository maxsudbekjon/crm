from rest_framework.generics import  get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Lead

class LeadHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id)

        # Lead yaratildi record
        lead_created = {
            "type": "lead_created",
            "text": "Lead yaratildi",
            "time": lead.created_at
        }

        timeline = []

        # 1. Status o'zgarishi
        for status in lead.status_history.all():
            timeline.append({
                "type": "status_change",
                "text": f"Status o‘zgartirildi: {status.new_status}",
                "time": status.changed_at
            })

        # 2. Qo'ng'iroqlar
        for call in lead.calls.all():
            timeline.append({
                "type": "call",
                "text": f"Qo‘ng‘iroq: {call.get_result_display()}",
                "time": call.call_time
            })

        # 3. SMSlar
        for sms in lead.sms_messages.all():
            timeline.append({
                "type": "sms",
                "text": "SMS jo‘natildi",
                "content": sms.content,
                "time": sms.sent_at
            })

        # 4. Izohlar
        for note in lead.notes.all():
            timeline.append({
                "type": "note",
                "text": note.content,
                "time": note.created_at
            })

        # Hammasini vaqt bo‘yicha tartiblash (eng yangisi yuqorida)
        timeline = sorted(timeline, key=lambda x: x["time"], reverse=True)

        # Lead yaratildi — har doim eng oxirida (timeline pastida)
        timeline.append(lead_created)

        return Response(timeline)