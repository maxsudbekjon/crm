from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django settings faylini ko‘rsatamiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Django settingsdan Celery konfiguratsiyasini yuklaymiz
app.config_from_object('django.conf:settings', namespace='CELERY')

# Barcha app’larda joylashgan tasks.py fayllarni avtomatik topadi
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')