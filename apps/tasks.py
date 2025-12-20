from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from django.db import transaction
from django.db.models import Count
from collections import defaultdict
from .utils import create_and_send_notification
from apps.models.operator import Operator
from apps.models.leads import Lead
from apps.models.penalty import Penalty
from apps.models.task_model import Task

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


#         operator

import logging
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from celery import shared_task
from .models import Lead, Operator, Enrollment

logger = logging.getLogger(__name__)

# ===============================================================
# 1️⃣ Lead commission task
# ===============================================================
from celery import shared_task
from django.utils import timezone
from apps.models import Lead, Operator
from decimal import Decimal

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_lead_commission(self, lead_id=None):
    try:
        leads = Lead.objects.filter(
            status='sold',
            commission_added=False
        )

        if lead_id:
            leads = leads.filter(id=lead_id)

        for lead in leads:
            operator = lead.operator
            if not operator or not lead.course:
                continue

            course_price = Decimal(lead.course.price)
            commission_rate = Decimal(str(operator.commission_rate))

            commission_amount = course_price * commission_rate

            operator.salary = F('salary') + commission_amount
            operator.save(update_fields=['salary'])

            lead.commission_added = True
            lead.save(update_fields=['commission_added'])

        return "Commission processed successfully"

    except Exception as exc:
        raise self.retry(exc=exc)

# -----------------------------------------------------
# 1) TASK DEADLINE PENALTY
# -----------------------------------------------------
@shared_task(name="apps.tasks.check_task_deadlines_penalty")
def check_task_deadlines_penalty():
    now = timezone.now()

    # deadline o‘tgan + 3 min, lekin penalty hali berilmagan tasklar
    tasks = Task.objects.filter(
        is_completed=False,
        penalty_given=False,
        deadline__lt=now - timezone.timedelta(minutes=3)
    )

    for task in tasks:
        operator = task.operator

        # Penalty yozamiz
        Penalty.objects.create(
            operator=operator,
            task=task,
            reason="Task deadline missed",
            points=1
        )

        # Operatorga jarima qo‘shamiz
        operator.penalty += 1
        operator.save(update_fields=['penalty'])

        # Taskga endi penalty berilmasligi uchun flag qo‘yiladi
        task.penalty_given = True
        task.save(update_fields=['penalty_given'])

    return f"{tasks.count()} ta task uchun penalty berildi."


@shared_task(name="apps.tasks.check_lead_no_call_penalty")
def check_lead_no_call_penalty():
    now = timezone.now()
    one_day_ago = now - timedelta(minutes=3)

    # 1 kundan beri umuman qo‘ng‘iroq bo‘lmagan leadlar
    leads = Lead.objects.filter(
        penalty_given=False,
        created_at__lte=one_day_ago,
        last_contact_date__isnull=True,
        operator__isnull=False
    ).select_related('operator')

    penalty_count = 0

    for lead in leads:
        operator = lead.operator

        if operator:  # Operator mavjud ekanligini tekshirish
            Penalty.objects.create(
                operator=operator,
                lead=lead,
                reason="Operator 2 daqiqa ichida qo'ng'iroq qilmadi",
                points=1
            )

            operator.penalty += 1
            operator.save(update_fields=["penalty"])

            lead.penalty_given = True
            lead.save(update_fields=["penalty_given"])

            penalty_count += 1

    return f"{leads.count} ta lead uchun 2 daqiqa qo'ng'iroq qilinmaganligi sababli penalty berildi."