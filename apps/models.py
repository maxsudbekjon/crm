from typing import Any
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from user.models import CustomUser


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Branch(Base):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Operator(Base):
    class StatusType(models.TextChoices):
        INTERN = 'Intern', 'Intern'
        WORKER = 'Worker', 'Worker'

    class StatusGender(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusType.choices)
    course = models.ManyToManyField('apps.Course', blank=True)  # Operator
    photo = models.ImageField(upload_to='operator_photos/', blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_rate = models.FloatField(default=0.05)  # default 5%
    penalty = models.IntegerField(default=0)
    gender = models.CharField(max_length=10, choices=StatusGender.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='operators')

    def __str__(self):
        if self.user.first_name or self.user.last_name:
            return f"{self.user.first_name or ''} {self.user.last_name or ''}".strip()
        return self.user.username

    def add_penalty(self, points=1):
        self.penalty += points
        self.save(update_fields=['penalty'])

from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)  # kurs nomi
    description = models.TextField(blank=True)  # kurs haqida
    price = models.FloatField()  # kurs narxi
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} | {self.price} so'm | {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['created_at']


class Enrollment(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=200)
    price_paid = models.FloatField()  # kurs narxi yoki chegirma bilan
    created_at = models.DateTimeField(auto_now_add=True)


class Lead(Base):
    class Status(models.TextChoices):
        NEED_CONTACT = "need_contact", "Need Contact"
        INFO_PROVIDED = "info_provided", "Information Provided"
        MEETING_SCHEDULED = "meeting_scheduled", "Meeting Scheduled"
        MEETING_CANCELLED = "meeting_cancelled", "Meeting Cancelled"
        COULD_NOT_CONTACT = "could_not_contact", "Could Not Contact"
        SOLD = "sold", "Sold"
        NOT_SOLD = "not_sold", "Not Sold"
        DID_NOT_SHOW_UP = "did_not_show_up", "Did Not Show Up"

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey('apps.Course', on_delete=models.SET_NULL, null=True, blank=True)  # Lead
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # bu borligini tekshir
    status = models.CharField(max_length=50, choices=Status.choices, default='new')
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    source = models.CharField(max_length=100, blank=True, null=True)
    demo_date = models.DateTimeField(blank=True, null=True)
    last_contact_date = models.DateTimeField(blank=True, null=True)


    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lead"
        verbose_name_plural = "Leadlar"


    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.price = None

    def __str__(self):
        return f"{self.full_name} ({self.get_status_display()})"

class Call(Base):
    class CallResult(models.TextChoices):
        SUCCESSFUL = "successful", "Successful"
        NO_ANSWER = "no_answer", "No Answer"
        BUSY = "busy", "Busy"
        WRONG_NUMBER = "wrong_number", "Wrong Number"
        FAILED = "failed", "Failed"

    operator = models.ForeignKey(
        Operator,
        on_delete=models.CASCADE,
        related_name="calls"
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="calls"
    )
    call_time = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    result = models.CharField(
        max_length=20,
        choices=CallResult.choices,
        default=CallResult.SUCCESSFUL
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-call_time']
        verbose_name = "Qo‘ng‘iroq"
        verbose_name_plural = "Qo‘ng‘iroqlar"

    def __str__(self):
        return f"{self.lead.full_name} bilan     ({self.get_result_display()})"

class Task(Base):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name="tasks")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    penalty_points = models.IntegerField(default=0)
    is_notified_10min = models.BooleanField(default=False)
    is_notified_5min = models.BooleanField(default=False)

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

class Penalty(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name="penalties")
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=255)
    points = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Jarima"
        verbose_name_plural = "Jarimalar"

    def apply_penalty(self):
        self.operator.add_penalty(self.points)

class SMS(Base):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="sms_messages"
    )
    operator = models.ForeignKey(
        "apps.Operator",
        on_delete=models.CASCADE,
        related_name="sent_sms"
    )
    provider_sms_sid = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"SMS to {self.lead.phone} by {self.operator.user.username if self.operator.user else 'unknown'}"


class Contract(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name="contracts")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="contracts")
    course_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.course_name
