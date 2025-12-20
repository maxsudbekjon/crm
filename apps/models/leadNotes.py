from django.db.models import DateTimeField, Model, ForeignKey, CASCADE, SET_NULL, TextField

from apps.models import Lead, Operator


class LeadNote(Model):
    lead = ForeignKey("apps.Lead", on_delete=CASCADE, related_name="notes")
    operator = ForeignKey(Operator, on_delete=SET_NULL, null=True)
    content = TextField()
    created_at = DateTimeField(auto_now_add=True)