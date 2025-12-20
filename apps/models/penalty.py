from django.db import models
from apps.models.leads import Lead
from apps.models import Operator
from apps.models.task_model import Task


class Penalty(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name="penalties")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="penalties", null=True, blank=True,)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=255)
    points = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Jarima"
        verbose_name_plural = "Jarimalar"

    def apply_penalty(self):
        self.operator.add_penalty(self.points)
