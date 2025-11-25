from django.db import models

class Click(models.Model):
    SOURCE_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('telegram', 'Telegram'),
        ('unknown', 'Unknown'),
    ]

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - {self.created_at}"
