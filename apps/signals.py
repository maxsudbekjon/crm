from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from apps.models import Lead, OperatorMonthlySalary, Call, Task, OperatorActivity
from django.db.models.signals import post_save


@receiver(pre_save, sender=Lead)
def apply_commission_on_sold(sender, instance: Lead, **kwargs):

    # Yangi Lead yaratilayotgan bo'lsa → chiqamiz
    if not instance.pk:
        return

    # Eski Lead holatini olish
    old = Lead.objects.get(pk=instance.pk)

    # Status o'zgarmayotgan bo'lsa → hech nima qilinmaydi
    if old.status == instance.status:
        return

    # Faqat SOLD bo'layotgan paytida ishlaydi
    if instance.status != Lead.Status.SOLD:
        return

    # Payment bo'lmasdan SOLD bo'lishiga ruxsat yo'q
    if not instance.payments.exists():
        return

    # Course bo'lishi shart
    if not instance.course:
        return

    # Komissiya allaqachon qo‘shilgan bo‘lsa → chiqamiz
    if instance.commission_added:
        return

    # Komissiya hisoblash
    commission_amount = Decimal(instance.course.price) * Decimal('0.10')

    today = timezone.now().date()
    month_start = today.replace(day=1)

    salary_obj, created = OperatorMonthlySalary.objects.get_or_create(
        operator=instance.operator,
        month=month_start
    )

    salary_obj.commission += commission_amount
    salary_obj.save()

    # Flag → keyingi to'lovlarda qayta komissiya qo‘shilmaydi
    instance.commission_added = True


@receiver(post_save, sender=Task)
def task_activity(sender, instance, created, **kwargs):
    if not created or not instance.operator:
        return

    OperatorActivity.objects.create(
        operator=instance.operator,
        lead=instance.lead,
        activity_type="task",
        description=f"Topshiriq yaratdi: {instance.lead.full_name}"
    )

@receiver(post_save, sender=Lead)
def lead_status_activity(sender, instance, created, **kwargs):
    if created or not instance.operator:
        return

    OperatorActivity.objects.create(
        operator=instance.operator,
        lead=instance,
        activity_type="status",
        description=f"{instance.full_name} statusi o‘zgardi → {instance.status}"
    )

@receiver(post_save, sender=Call)
def call_activity(sender, instance, created, **kwargs):
    if not created:
        return

    OperatorActivity.objects.create(
        operator=instance.operator,
        lead=instance.lead,
        activity_type="call",
        description=f"Lead bilan bog‘landi: {instance.lead.full_name}"
    )
