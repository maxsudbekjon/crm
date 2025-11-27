from django.db import models

from apps.models.leads import Lead
from apps.models.operator import Operator


class Contract(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name="contracts")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="contracts")
    course_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.course_name