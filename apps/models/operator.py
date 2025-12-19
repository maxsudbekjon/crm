from django.db import models
from Auth.models import CustomUser
from apps.models.base import Base
from apps.models.branch import Branch

class Operator(Base):
    class StatusType(models.TextChoices):
        INTERN = 'Intern', 'Intern'
        WORKER = 'Worker', 'Worker'

    class StatusGender(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=StatusType.choices)
    photo = models.ImageField(upload_to='operator_photos/', blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_rate = models.FloatField(default=0.05)
    penalty = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=StatusGender.choices)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='operators')

    def __str__(self):
        return self.user.username