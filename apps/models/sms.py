from django.db import models

from apps.models.base import Base
from apps.models.leads import Lead


class SMS(Base):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="sms_messages"
    )
    operator = models.ForeignKey(
        "apps.Operator",
        on_delete=models.CASCADE,
        related_name="sent_sms"
    )
    provider_sms_sid = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"SMS to {self.lead.phone} by {self.operator.user.username if self.operator.user else 'unknown'}"

