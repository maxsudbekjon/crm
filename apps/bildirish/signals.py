import logging
from decimal import Decimal
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.models import Lead, Operator, Task, Penalty

logger = logging.getLogger(__name__)

# Bonus signal (Lead)
@receiver(post_save, sender=Lead)
def apply_bonus_on_sold(sender, instance: Lead, **kwargs):
    if instance.status.lower() != 'sotildi':
        return

    if getattr(instance, 'bonus_given', False):
        return

    operator = getattr(instance, 'operator', None)
    if not operator:
        logger.warning(f"Lead {instance.id} ga operator biriktirilmagan, bonus berilmadi.")
        return

    try:
        with transaction.atomic():
            payments = Payment.objects.filter(lead=instance)
            total_amount = sum([p.amount for p in payments])

            percent = getattr(operator, 'bonus_percent', 0)
            bonus = Decimal(total_amount) * Decimal(percent) / Decimal(100)

            operator.salary += bonus
            operator.save(update_fields=['salary'])

            instance.bonus_given = True
            instance.save(update_fields=['bonus_given'])

            logger.info(f"Bonus {bonus} qo'shildi Operator {operator.id} ga Lead {instance.id} orqali.")
    except Exception as e:
        logger.exception(f"Error applying bonus for Lead {instance.id}: {e}")


# Penalty signal (Task)
@receiver(post_save, sender=Task)
def check_overdue_task(sender, instance: Task, created: bool = False, **kwargs) -> None:
    if instance.is_completed or instance.deadline >= timezone.now():
        return

    operator: Operator = getattr(instance, "operator", None)
    if operator is None:
        logger.warning(f"[Penalty] Task {instance.id} has no operator. Penalty not applied.")
        return

    if Penalty.objects.filter(task=instance, operator=operator).exists():
        logger.info(f"[Penalty] Task {instance.id} already has a penalty for operator {operator.id}. Skipping.")
        return

    try:
        with transaction.atomic():
            penalty = Penalty.objects.create(
                operator=operator,
                task=instance,
                reason="Topshiriq vaqtida bajarilmadi",
                points=1
            )

            if hasattr(instance, "penalty_points"):
                instance.penalty_points = (instance.penalty_points or 0) + penalty.points
                instance.save(update_fields=["penalty_points"])

            if hasattr(operator, "add_penalty"):
                operator.add_penalty(points=penalty.points)

            logger.info(f"[Penalty] Applied {penalty.points} point(s) for Task {instance.id} to Operator {operator.id}")
    except Exception as e:
        logger.exception(f"[Penalty][Error] Failed to apply penalty for Task {instance.id}: {e}")
