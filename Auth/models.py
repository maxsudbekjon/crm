from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_OPERATOR = 'operator'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_OPERATOR, 'Operator')
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ADMIN)

    age = models.PositiveIntegerField(blank=True, null=True)
    address = models.CharField(max_length=160, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_operator(self):
        return self.role == self.ROLE_OPERATOR

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def full_name(self):
        return self.first_name + self.last_name


