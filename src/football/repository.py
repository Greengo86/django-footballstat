from django.db.models import QuerySet

from football import helpers
from football.models import Play


def get_current_season_plays() -> QuerySet:
    date = helpers.get_date_start_season()
    _filter = {'date__gte': date, 'team_home__active': True, 'team_away__active': True}
    return Play.objects.select_related('team_home', 'team_away', 'league').filter(**_filter)


