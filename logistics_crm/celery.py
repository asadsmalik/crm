import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logistics_crm.settings")
app = Celery("logistics_crm")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = 'US/Pacific'
app.autodiscover_tasks()
