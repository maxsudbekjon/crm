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
            create_and_send_notification(operator, message, data={"task_id": task.id, "rem": 10})
            task.is_notified_10min = True
            task.save(update_fields=['is_notified_10min'])

        elif timedelta(minutes=4) < time_left <= timedelta(minutes=5) and not task.is_notified_5min:
            message = f"'{task.title}' topshirig'ingizga 5 daqiqa qoldi!"
            create_and_send_notification(operator, message, data={"task_id": task.id, "rem": 5})
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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_lead_commission(self, lead_id=None):
    try:
        # 1️⃣ Agar bitta lead berilgan bo‘lsa — faqat shuni ishlaymiz
        if lead_id:
            leads = Lead.objects.filter(id=lead_id, status='sold')
        else:
            # 2️⃣ Aks holda — barcha sold leadlarni olamiz
            leads = Lead.objects.filter(status='sold')

        for lead in leads:
            operator = lead.operator

            # operator yo‘q bo‘lsa davom etamiz
            if not operator:
                continue

            # 3️⃣ Course dan narx olish
            course_price = lead.course.price if lead.course else 0

            # 4️⃣ Operatorning commission rate
            commission_rate = operator.commission_rate or 0
            # 5️⃣ Komissiya hisoblash
            commission_amount = course_price * commission_rate

            # 6️⃣ Operatorga qo‘shish
            operator.salary += commission_amount
            operator.save(update_fields=['salary'])

        return "Commission hisoblandi!"

    except Exception as exc:
        raise self.retry(exc=exc)


# ===============================================================
# 2️⃣ Barcha sold leadlar uchun task
# ===============================================================
@shared_task(name="apps.tasks.process_lead_commission_all_sold")
def process_lead_commission_all_sold():
    try:
        sold_ids = Lead.objects.filter(status='sold').values_list('id', flat=True)
        if not sold_ids:
            logger.info("Sold lead topilmadi.")
            return

        for lead_id in sold_ids:
            if lead_id is not None:
                process_lead_commission.delay(int(lead_id))

        logger.info(f"{len(sold_ids)} ta sold lead commission taskiga yuborildi.")

    except Exception as exc:
        logger.error(f"process_lead_commission_all_sold xatosi: {exc}")


# ===============================================================
# 3️⃣ Salary + penalty qayta hisoblash (Enrollments asosida)
# ===============================================================
@shared_task(name="apps.tasks.update_all_operator_salary_penalty")
def update_all_operator_salary_penalty():
    try:
        operators = Operator.objects.all()
        for op in operators:
            enrollments = Enrollment.objects.filter(operator=op)

            total_commission = sum(
                Decimal(e.price_paid) * Decimal(getattr(op, "commission_rate", 0.10))
                for e in enrollments
            )

            with transaction.atomic():
                op.salary = total_commission
                op.penalty = enrollments.count()
                op.save(update_fields=['salary', 'penalty'])

            logger.info(f"Operator {op.id}: salary={op.salary}, penalty={op.penalty}")

    except Exception as exc:
        logger.error(f"update_all_operator_salary_penalty xatosi: {exc}")


# ===============================================================
# 4️⃣ Auto penalty checker (har operatorga +1 penalty)
# ===============================================================
@shared_task(name="apps.tasks.auto_penalty_checker")
def auto_penalty_checker():
    try:
        operators = Operator.objects.all()
        for op in operators:
            op.penalty += 1
            op.save(update_fields=['penalty'])

        logger.info("Auto penalty checker ishladi.")

    except Exception as exc:
        logger.error(f"auto_penalty_checker xatosi: {exc}")


# ===============================================================
# 5️⃣ Bulk penalty (barcha operatorlarga)
# ===============================================================
@shared_task(name="apps.tasks.add_penalty_to_all_bulk")
def add_penalty_to_all_bulk(points: int = 1):
    try:
        updated = Operator.objects.update(penalty=F('penalty') + points)
        logger.info(f"Bulk penalty qo‘shildi: {points}, updated={updated}")

    except Exception as exc:
        logger.error(f"add_penalty_to_all_bulk xatosi: {exc}")


# ===============================================================
# 6️⃣ Enrollment commission task (operatorga foiz qo‘shish)
# ===============================================================
@shared_task
def add_commission_task(enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id)
    operator = enrollment.operator
    if operator:
        commission_amount = enrollment.price_paid * operator.commission_rate / 100
        operator.commission_total += commission_amount
        operator.save()
        logger.info(f"Operator {operator.id} ga {commission_amount} commission qo‘shildi.")


# ===============================================================
# 7️⃣ Specific operatorga penalty qo‘shish task
# ===============================================================
@shared_task(name="apps.tasks.add_penalty")
def add_penalty(operator_id: int, points: int = 1):
    try:
        op = Operator.objects.get(id=operator_id)
        op.penalty += points
        op.save(update_fields=['penalty'])
        logger.info(f"Operator {op.id} ga {points} ball penalty qo‘shildi")
    except Operator.DoesNotExist:
        logger.warning(f"Operator {operator_id} topilmadi")