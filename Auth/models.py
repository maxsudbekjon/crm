from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.ROLE_ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone, password, **extra_fields)

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
    phone = models.CharField(max_length=15, unique=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_operator(self):
        return self.role == self.ROLE_OPERATOR

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def full_name(self):
        return self.first_name + self.last_name
