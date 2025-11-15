from celery import shared_task
from apps.models import Lead, Operator
import itertools
import random

@shared_task
def distribute_leads_task():
    leads = list(Lead.objects.filter(operator__isnull=True))
    if not leads:
        return "Biriktirilmagan leadlar yo‘q."

    operators = Operator.objects.filter(status='Worker')
    if not operators.exists():
        return "Tasdiqlangan operatorlar yo‘q."

    eligible_ops = []
    for op in operators:
        active_leads = op.leads.filter(status__in=['New', 'Info_given']).count()
        active_tasks = op.tasks.filter(completed=False).count()
        if active_leads > 0 or active_tasks > 0:
            continue
        penalty_count = op.penalties.count()
        weight = max(1, 5 - penalty_count)  # Penalty ko‘p bo‘lsa, kamroq vazn
        eligible_ops.extend([op] * weight)

    if not eligible_ops:
        return "Yaroqli operatorlar topilmadi."

    random.shuffle(eligible_ops)
    ops_cycle = itertools.cycle(eligible_ops)

    assigned = []
    for lead in leads:
        operator = next(ops_cycle)
        lead.operator = operator
        lead.save()
        assigned.append({
            "lead": lead.full_name,
            "operator": operator.full_name
        })

    return f"{len(assigned)} ta lead operatorlarga taqsimlandi."
