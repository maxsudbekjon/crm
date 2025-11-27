from django.db import models

from apps.models.base import Base


class Branch(Base):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name
