from django.db import models

from apps.models.base import Base
from apps.models.leads import Lead
from apps.models.operator import Operator


class Call(Base):
    class CallResult(models.TextChoices):
        SUCCESSFUL = "successful", "Successful"
        NO_ANSWER = "no_answer", "No Answer"
        BUSY = "busy", "Busy"
        WRONG_NUMBER = "wrong_number", "Wrong Number"
        FAILED = "failed", "Failed"

    operator = models.ForeignKey(
        Operator,
        on_delete=models.CASCADE,
        related_name="calls"
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="calls"
    )
    call_time = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    result = models.CharField(
        max_length=20,
        choices=CallResult.choices,
        default=CallResult.SUCCESSFUL
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-call_time']
        verbose_name = "Qo‘ng‘iroq"
        verbose_name_plural = "Qo‘ng‘iroqlar"

    def __str__(self):
        return f"{self.lead.full_name} bilan {self.operator.user.get_full_name()} ({self.get_result_display()})"
