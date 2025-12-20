from django.db import models
from django.utils import timezone
from apps.models import Operator, Lead


class OperatorActivity(models.Model):
    ACTIVITY_TYPES = (
        ("call", "Lead bilan bog‘landim"),
        ("meeting", "Uchrashuv belgiladim"),
        ("task", "Topshiriq yaratdim"),
        ("status", "Status o‘zgartirdim"),
    )

    operator = models.ForeignKey(
        Operator,
        on_delete=models.CASCADE,
        related_name="activities"
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities"
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.operator} - {self.activity_type}"

    @property
    def lead_full_name(self):
        return self.lead.full_name if self.lead else "-"