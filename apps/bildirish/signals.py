from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.models import Lead, enrollment
from apps.tasks import process_lead_commission, add_penalty


@receiver(pre_save, sender=Lead)
def cache_old_status(sender, instance, **kwargs):
    if instance.id:
        instance._old_status = lead.objects.filter(id=instance.id)\
                                .values_list("status", flat=True).first()
    else:
        instance._old_status = None


@receiver(post_save, sender=Lead)
def trigger_commission(sender, instance, created, **kwargs):
    # Status "sold" ga o‘zgarganda task ishga tushadi
    if instance._old_status != "sold" and instance.status == "sold":
        process_lead_commission.delay(instance.id)
        print(f"Task ishga tushdi → Lead {instance.id}")

#             Jarima


from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.models import Lead

@receiver(post_save, sender=Lead)
def trigger_penalty(sender, instance, created, **kwargs):
    # Masalan, demo_date dan kech kelgan bo‘lsa operatorga jarima
    if instance.demo_date and instance.demo_date < instance.last_contact_date:
        if instance.operator:
            add_penalty.delay(instance.operator.id, 10)  # 10 ball jarima


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Enrollment)
def add_operator_commission(sender, instance, created, **kwargs):
    if created:
        # operatorni aniqlaymiz
        operator = instance.course.operator  # agar Course modelida operator bor bo‘lsa
        if operator:
            commission_percent = 0.5  # 10%
            commission_amount = instance.price * commission_percent
            operator.total_lead_amount += commission_amount
            operator.save()
