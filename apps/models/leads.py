from django.db import models

from apps.models.base import Base
from apps.models.operator import Operator


class Lead(Base):
    class Status(models.TextChoices):
        NEED_CONTACT = "need_contact", "Need Contact"
        INFO_PROVIDED = "info_provided", "Information Provided"
        MEETING_SCHEDULED = "meeting_scheduled", "Meeting Scheduled"
        MEETING_CANCELLED = "meeting_cancelled", "Meeting Cancelled"
        COULD_NOT_CONTACT = "could_not_contact", "Could Not Contact"
        SOLD = "sold", "Sold"
        NOT_SOLD = "not_sold", "Not Sold"
        DID_NOT_SHOW_UP = "did_not_show_up", "Did Not Show Up"

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=50, choices=Status.choices, default='new')
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    source = models.CharField(max_length=100, blank=True, null=True)
    demo_date = models.DateTimeField(blank=True, null=True)
    last_contact_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lead"
        verbose_name_plural = "Leadlar"

    def __str__(self):
        return f"{self.full_name} ({self.get_status_display()})"
