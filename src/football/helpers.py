from footballstat import settings
from datetime import datetime, timedelta
import time


def get_date_start_season():
    '''
    Вернем дату начала текущего сезона
    '''
    date_time = datetime.now() - timedelta(days=365)
    # return str(datetime.date(date_time).year) + '-' + settings.DATE_END_SEASON
    return str(2017) + '-' + settings.DATE_END_SEASON


def time_track(func):
    def surrogate(*args, **kwargs):
        started_at = time.time()

        result = func(*args, **kwargs)

        ended_at = time.time()
        elapsed = round(ended_at - started_at, 4)
        print(f'Функция работала {elapsed} секунд(ы)')
        return result
    return surrogate
