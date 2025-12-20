from django.db import models
from apps.models import Lead, Operator, Course


class Payment(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    commission_added = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment {self.id} - {self.lead.full_name} {self.amount}"

    class Meta:
        ordering = ['-created_at']


class OperatorMonthlySalary(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='monthly_salaries')
    month = models.DateField(help_text='First day of month, e.g. 2025-12-01')
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('operator', 'month')
        ordering = ['-month']

    @property
    def total_salary(self):
        return self.commission or 0


    def __str__(self):
        return f"{self.operator} - {self.month} - {self.commission}"
