import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# установить модуль настроек Django по умолчанию для программы «сельдерей».
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'footballstat.settings')
app = Celery('stats_parser')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    'send-print-every-single-minute': {
        'task': 'stats_parser.tasks.send_print',
        'schedule': crontab(),  # change to `crontab(minute=0, hour=0)` if you want it to run daily at midnight
        'args': (['F'])
    },
}