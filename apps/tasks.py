from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from .models import Task, Operator
from .utils import create_and_send_notification

@shared_task
def check_task_deadlines():
    now = timezone.now()
    tasks = Task.objects.filter(is_completed=False)

    for task in tasks:
        operator = task.operator  # to'g'ridan-to'g'ri Operator
        if not operator:
            continue

        time_left = task.deadline - now

        # 10 daqiqa qolganda
        if timedelta(minutes=9) < time_left <= timedelta(minutes=10) and not task.is_notified_10min:
            message = f"'{task.title}' topshirig'ingizga 10 daqiqa qoldi!"
            create_and_send_notification(operator, message, data={"task_id": task.id, "rem": 10})
            task.is_notified_10min = True
            task.save(update_fields=['is_notified_10min'])

        # 5 daqiqa qolganda
        elif timedelta(minutes=4) < time_left <= timedelta(minutes=5) and not task.is_notified_5min:
            message = f"'{task.title}' topshirig'ingizga 5 daqiqa qoldi!"
            create_and_send_notification(operator, message, data={"task_id": task.id, "rem": 5})
            task.is_notified_5min = True
            task.save(update_fields=['is_notified_5min'])
