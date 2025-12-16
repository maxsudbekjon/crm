from django.db.models import ForeignKey, Model, CASCADE, CharField, DateTimeField



class LeadStatusHistory(Model):
    lead = ForeignKey(
        "apps.Lead",
        on_delete=CASCADE,
        related_name="status_history"
    )
    old_status = CharField(max_length=50, blank=True, null=True)
    new_status = CharField(max_length=50)
    changed_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lead.full_name}: {self.old_status} → {self.new_status}"