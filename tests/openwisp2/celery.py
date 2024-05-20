import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'immunity2.settings')

app = Celery('immunity2')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
