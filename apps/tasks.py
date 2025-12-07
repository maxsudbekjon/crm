from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from django.db import transaction
from django.db.models import Count
from collections import defaultdict

from .models import Lead, Operator, Task
from .utils import create_and_send_notification

# =========================
# Leadlarni operatorlarga taqsimlash
# =========================
@shared_task
def distribute_leads_task():
    debug_info = {
        'total_unassigned_leads': 0,
        'total_operators_checked': 0,
        'eligible_operators': 0,
        'operator_details': [],
        'distribution': [],
        'summary': {}
    }

    # Step 1: Get unassigned leads
    leads = list(Lead.objects.filter(operator__isnull=True))
    debug_info['total_unassigned_leads'] = len(leads)

    if not leads:
        debug_info['summary']['message'] = "No unassigned leads found."
        return debug_info

    # Step 2: Get verified operators
    operators = Operator.objects.filter(status="Worker").annotate(
        total_leads_count=Count('leads')
    )
    debug_info['total_operators_checked'] = operators.count()

    if not operators.exists():
        debug_info['summary']['message'] = "No verified operators found."
        return debug_info

    # Step 3: Filter eligible operators
    eligible = []

    for op in operators:
        operator_info = {
            'id': op.id,
            'name': op.user.full_name,
            'eligible': False,
            'reason': None,
            'total_leads_handled': op.total_leads_count
        }

        active_leads = op.leads.filter(status__in=["need_contact"]).count()
        active_tasks = op.tasks.filter(is_completed=False).count()

        if active_leads > 0:
            operator_info['reason'] = f"Has {active_leads} active lead(s)"
        elif active_tasks > 0:
            operator_info['reason'] = f"Has {active_tasks} unfinished task(s)"
        else:
            operator_info['eligible'] = True
            operator_info['reason'] = "Eligible for new leads"
            eligible.append(op)

        debug_info['operator_details'].append(operator_info)

    debug_info['eligible_operators'] = len(eligible)
    if not eligible:
        debug_info['summary']['message'] = "No eligible operators found."
        return debug_info

    # Step 4: Sort operators by total leads handled
    eligible = sorted(eligible, key=lambda o: o.total_leads_count)

    # Step 5: Round-robin distribution
    lead_count = len(leads)
    op_count = len(eligible)
    leads_per_operator = lead_count // op_count
    remaining_leads = lead_count % op_count

    debug_info['summary']['leads_per_operator'] = leads_per_operator
    debug_info['summary']['remaining_leads'] = remaining_leads

    with transaction.atomic():
        distribution_count = defaultdict(int)
        op_index = 0

        for i, lead in enumerate(leads):
            operator = eligible[op_index]
            lead.operator = operator
            lead.save()
            distribution_count[operator.id] += 1

            debug_info['distribution'].append({
                'lead_id': lead.id,
                'lead_name': lead.full_name,
                'operator_id': operator.id,
                'operator_name': operator.user.full_name,
                'sequence': i + 1
            })
            op_index = (op_index + 1) % op_count

    debug_info['summary']['total_assigned'] = len(leads)
    debug_info['summary']['assignments_per_operator'] = [
        {
            'operator_id': op.id,
            'operator_name': op.user.full_name,
            'leads_assigned': distribution_count[op.id],
            'previous_total': op.total_leads_count,
            'new_total': op.total_leads_count + distribution_count[op.id]
        }
        for op in eligible
    ]
    debug_info['summary']['message'] = (
        f"Successfully distributed {len(leads)} lead(s) to {op_count} operator(s)."
    )

    return debug_info


# =========================
# Task deadline notification
# =========================
@shared_task
def check_task_deadlines():
    now = timezone.now()
    tasks = Task.objects.filter(is_completed=False)

    for task in tasks:
        operator = task.operator
        if not operator:
            continue

        time_left = task.deadline - now

        if timedelta(minutes=9) < time_left <= timedelta(minutes=10) and not task.is_notified_10min:
            message = f"'{task.title}' topshirig'ingizga 10 daqiqa qoldi!"
            create_and_send_notification(operator, message, data={ "rem": 10}, task=task)
            task.is_notified_10min = True
            task.save(update_fields=['is_notified_10min'])

        elif timedelta(minutes=4) < time_left <= timedelta(minutes=5) and not task.is_notified_5min:
            message = f"'{task.title}' topshirig'ingizga 5 daqiqa qoldi!"
            create_and_send_notification(operator, message, data={"rem": 5}, task=task)
            task.is_notified_5min = True
            task.save(update_fields=['is_notified_5min'])
