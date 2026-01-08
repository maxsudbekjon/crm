from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from apps.models import Lead, OperatorMonthlySalary


@receiver(pre_save, sender=Lead)
def apply_commission_on_sold(sender, instance: Lead, **kwargs):

    if not instance.pk:
        return
    old = Lead.objects.get(pk=instance.pk)

    if old.status == instance.status:
        return

    if instance.status != Lead.Status.SOLD:
        return

    if not instance.payments.exists():
        return

    if not instance.course:
        return

    if instance.commission_added:
        return
    commission_amount = Decimal(instance.course.price) * Decimal('0.10')

    today = timezone.now().date()
    month_start = today.replace(day=1)

    salary_obj, created = OperatorMonthlySalary.objects.get_or_create(
        operator=instance.operator,
        month=month_start
    )

    salary_obj.commission += commission_amount
    salary_obj.save()

    instance.commission_added = True