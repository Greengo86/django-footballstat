from football import helpers
from football.models import Play, Team


def get_current_seasson_plays_by_league(league_id, date=helpers.get_date_start_season(), with_related=None):
    _filter = {'league__id': league_id, 'date__gte': date, 'home_team__active': True, 'away_team__active': True}
    plays = Play.objects.filter(**_filter)
    if with_related is not None:
        plays.select_related(with_related)
    return plays


def get_teams(league_id, with_related=None):
    _filter = {'active': True, 'league__id': league_id}
    teams = Team.objects.filter(**_filter)
    if with_related is not None:
        teams.select_related(with_related)
    return teams


