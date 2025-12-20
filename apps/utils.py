from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, Operator

def create_and_send_notification(operator: Operator, message, task=None ,data=None):
    """
    Operator uchun notification yaratadi va WebSocket orqali yuboradi
    """
    if not operator:
        print("❌ Warning: No operator provided")
        return None

    # Notification yaratish
    try:
        notif = Notification.objects.create(
            user=operator,  # faqat Operator
            task=task,
            message=message,
            data=data or {}
        )
        print(f"✅ Notification created: ID={notif.id} for operator={operator.user.username}")
    except Exception as e:
        print(f"❌ Error creating notification: {e}")
        return None

    # WebSocket orqali yuborish
    channel_layer = get_channel_layer()
    payload = {
        "type": "send_notification",
        "message": message,
        "data": data or {},
        "notification_id": notif.id,
        "created_at": timezone.localtime(notif.created_at).isoformat(),
    }

    try:
        async_to_sync(channel_layer.group_send)(
            f"user_{operator.id}",
            payload
        )
        print(f"✅ WebSocket notification sent to operator_{operator.id}")
    except Exception as e:
        print(f"❌ Error sending WebSocket notification: {e}")

    return notif

from datetime import date, datetime


def first_day_of_month(dt: date):
    return date(dt.year, dt.month, 1)


def get_or_create_operator_salary(operator, dt):
    """Oyning birinchi kuni bo‘yicha maosh yozuvi"""
    from apps.models import OperatorMonthlySalary

    month = first_day_of_month(dt)

    salary, created = OperatorMonthlySalary.objects.get_or_create(
        operator=operator,
        month=month,
    )
    return salary

from datetime import date, timedelta
from django.utils.timezone import make_aware
import calendar


def last_day_of_month(dt: date):
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return date(dt.year, dt.month, last_day)


from datetime import datetime, time

def month_range(day):
    start = day.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)

    start_dt = make_aware(datetime.combine(start, time.min))
    end_dt = make_aware(datetime.combine(end, time.max))

    return start_dt, end_dt
