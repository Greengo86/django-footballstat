import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# установить модуль настроек Django по умолчанию для программ celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'footballstat.settings')
app = Celery('stats_parser')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    'test': {
        'task': 'stats_parser.tasks.go_parse',
        'schedule': crontab(minute='*/1'),  # change to `crontab(minute=0, hour=0)` if you want it to run daily at midnight
        'args': (['last_plays'])
    },
    'parse-team-before-season': {
        'task': 'stats_parser.tasks.go_parse',
        'schedule': crontab(minute=0, hour='*/6', day_of_month='30', month_of_year='7'),
        # Execute hour divisible by 6 and Execute on the 30 of July every year
        'args': (['teams'])
    },
    'parse-last-plays': {
        'task': 'stats_parser.tasks.go_parse',
        'schedule': crontab(minute='*/10', hour='18,19,20,21,22,23,0,1', day_of_week='fri,sat,sun,mon'),
        # Execute every 10 minutes on 18, 19, 20, 21, 22, 23, 0, 1 hours!
        'args': (['last_plays'])
    },
    'parse-all-plays-is-one-time': {
        'task': 'stats_parser.tasks.go_parse',
        'schedule': crontab(minute=0, hour=0, day_of_month='30', month_of_year='7'),
        # Первичная инициализация базы - парсинг игр начиная с 14 года по текущий момент. Наверное, запущу 1 раз руками
        'args': (['all_plays'])
    },
}