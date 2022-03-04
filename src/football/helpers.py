from footballstat import settings
from datetime import datetime, timedelta
import time


def get_date_start_season() -> str:
    '''
    Вернем дату начала текущего сезона
    '''
    date_now = datetime.now()
    date_new_season = datetime.strftime(date_now, '%Y') + '-' + settings.DATE_END_SEASON
    datetime_now = datetime.strftime(date_now, '%Y-%m-%d')
    if datetime_now >= date_new_season:
        return date_new_season
    else:
        previous_year = datetime.strftime(date_now - timedelta(days=365), '%Y')
        return previous_year + '-' + settings.DATE_END_SEASON


def time_track(func):
    def surrogate(*args, **kwargs):
        started_at = time.time()

        result = func(*args, **kwargs)

        ended_at = time.time()
        elapsed = round(ended_at - started_at, 4)
        print(f'Функция работала {elapsed} секунд(ы)')
        return result

    return surrogate


def get_team_emblem(plays: list) -> dict:
    name_2_emblem = {}
    name_2_emblem.update(
        {play.team_home.name: play.team_home.emblem for play in plays if play.team_home.name not in name_2_emblem})
    name_2_emblem.update(
        {play.team_away.name: play.team_away.emblem for play in plays if play.team_away.name not in name_2_emblem})

    return name_2_emblem
