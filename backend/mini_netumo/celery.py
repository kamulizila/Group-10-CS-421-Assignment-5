import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_netumo.settings')

# Create Celery app
app = Celery('mini_netumo')

# Load config from Django settings using 'CELERY_' namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in your installed apps
app.autodiscover_tasks()

# Use django-celery-beat scheduler (only needed if using DatabaseScheduler)
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

# Schedule periodic tasks (if NOT using django-celery-beat GUI)
app.conf.beat_schedule = {
    'check-targets-every-5-minutes': {
        'task': 'api.tasks.check_targets_status',
        'schedule': crontab(minute='*/5'),  # every 5 minutes
    },
    'check-ssl-domain-every-day': {
        'task': 'api.tasks.check_ssl_and_domain_expiry',
        'schedule': crontab(hour=0, minute=0),  # every day at midnight
    },
}
