from collections import defaultdict

from django.shortcuts import redirect

from apps.forms import EnrollmentForm
from apps.models import Lead, Operator, enrollment


from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from django.db import transaction
from django.db.models import Count
from collections import defaultdict

from .models import Lead, Operator, Task

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

@shared_task(name="apps.tasks.process_lead_commission_all_sold")
def process_lead_commission_all_sold():
    """
    Barcha sold leadlar bo'yicha operatorlarga salary/komissiya hisoblaydi.
    """
    # 1) Barcha sold leadlar va operatori mavjud bo‘lganlarini olamiz
    sold_leads = Lead.objects.filter(status="sold", operator__isnull=False)

    # 2) Har bir lead bo‘yicha operator salary qo‘shiladi
    for lead in sold_leads:
        Operator.objects.filter(id=lead.operator.id).update(
            salary=F('salary') + lead.commission_amount
        )
        print(f"Operator {lead.operator.id}: +{lead.commission_amount} added for Lead {lead.id}")

    return f"Processed {sold_leads.count()} sold leads"

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import F
import logging

from apps.models import Task, Operator

logger = logging.getLogger(__name__)

@shared_task(name="apps.tasks.auto_deadline_penalty_checker")
def auto_deadline_penalty_checker():
    """
    Deadline'dan 3 minut o'tgan, lekin hali bajarilmagan
    va hali penalty berilmagan tasklar uchun operatorga penalty +1.
    Race conditionlarni oldini olish uchun select_for_update va transaction ishlatiladi.
    """
    try:
        now = timezone.now()
        threshold = now - timezone.timedelta(minutes=3)

        # 1) Oxirgi holatlarni log qilamiz (debug uchun)
        logger.info(f"Running auto_deadline_penalty_checker at {now}; threshold={threshold}")

        # 2) Olamiz: hali bajarilmagan, deadline 3+ minut o'tgan, penalty berilmagan
        qs = Task.objects.filter(
            is_completed=False,
            deadline__lt=threshold,
            penalty_given=False
        )

        if not qs.exists():
            logger.info("No expired tasks requiring penalty.")
            return

        # 3) Xavfsiz yangilash: select_for_update bilan zanjir
        with transaction.atomic():
            # select_for_update bilan rowlarni qulflaymiz
            tasks = list(qs.select_for_update(nowait=False))

            for task in tasks:
                # yana tekshirib olinadi (double-check)
                if task.is_completed or task.penalty_given:
                    continue

                # operatorga atomic increment qilamiz
                Operator.objects.filter(pk=task.operator_id).update(penalty=F('penalty') + 1)

                # task uchun penalty flag ni yangilaymiz
                Task.objects.filter(pk=task.pk).update(penalty_given=True)

                logger.info(f"Penalty qo‘shildi: Operator={task.operator_id}, Task={task.id}")

        logger.info("Auto deadline penalty checker completed successfully.")

    except Exception as exc:
        logger.exception(f"auto_deadline_penalty_checker xatosi: {exc}")
