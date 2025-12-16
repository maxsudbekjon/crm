from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.models import Course
from apps.models.leads import Lead
User = get_user_model()


class DemoLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="demo_lessons")
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="demo_lessons")
    start_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.title} - {self.start_at.strftime('%Y-%m-%d %H:%M')}"


class LeadDemoAssignment(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="demo_assignments")
    demo = models.ForeignKey(DemoLesson, on_delete=models.CASCADE, related_name="lead_assignments")
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="assigned_demo_lessons")
    assigned_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.lead} -> {self.demo}"