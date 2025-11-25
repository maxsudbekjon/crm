from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, Operator

def create_and_send_notification(operator: Operator, message, data=None):
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
