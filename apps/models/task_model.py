from django.db import models
from apps.models.base import Base
from apps.models.leads import Lead
from apps.models.operator import Operator
from Auth.models import CustomUser
from django.utils import timezone


class Task(Base):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name="tasks")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_notified_10min = models.BooleanField(default=False)
    is_notified_5min = models.BooleanField(default=False)
    penalty_given = models.BooleanField(default=False)  # 🔥 yangi

    def mark_completed(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.is_notified_10min = False
        self.is_notified_5min = False
        self.save(update_fields=['is_completed', 'completed_at', 'is_notified_10min', 'is_notified_5min'])

    def __str__(self):
        return f"{self.title} ({'Bajarilgan' if self.is_completed else 'Bajarilmagan'})"

class Notification(Base):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message = models.TextField()
    data = models.JSONField(null=True, blank=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"Notif to {self.user.username}: {self.message[:50]}"