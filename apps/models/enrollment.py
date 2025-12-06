from django.db import models
from apps.models import Operator
from apps.models.course import Course


class Enrollment(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=200)
    price_paid = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
