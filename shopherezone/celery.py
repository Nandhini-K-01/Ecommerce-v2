from __future__ import absolute_import, unicode_literals # Ensures compatibility between Python 2 and 3 (must for older codebases)
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopherezone.settings')

app = Celery('shopherezone')
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix. Loads Celery-related configurations from Django's settings under the CELERY_ namespace.
app.config_from_object(settings, namespace='CELERY')


# Celery Beat Settings
app.conf.beat_schedule = {
    "send-mail-everyday-at-7am": {
        'task': 'api.tasks.send_mail_func',
        'schedule': crontab(hour=7)
    },
    "update-subscription-status-at-12am": {
        'task': 'api.tasks.update_subscription_status',
        'schedule': crontab(hour=0)
    }
}


# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# Defines a simple task that prints the request information for debugging.
# @app.task(bind=True): Binding allows access to task context via self.
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')