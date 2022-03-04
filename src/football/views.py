from itertools import groupby

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from football.models import Play
from . import stat_facts, tournament_table, helpers
from football import repository


def main(request):
    stats_facts, table_tournament, league_id_2_name, plays_grouped_by_league_id, team_emblems = {}, {}, {}, {}, {}
    ungrouped_plays = sorted(repository.get_current_season_plays(), key=lambda x: x.league_id)
    for league_id, grouped in groupby(ungrouped_plays, key=lambda x: x.league_id):
        list_plays = [play for play in grouped]
        team_emblems.update(helpers.get_team_emblem(list_plays))
        plays_grouped_by_league_id[league_id] = list_plays

    for league_id, plays in plays_grouped_by_league_id.items():
        league_id_2_name.update({league_id: plays[0].league.name})
        get_stats, get_table = stat_facts.get_factory(), tournament_table.get_factory()
        stats_facts.update({league_id_2_name[league_id]: get_stats(plays)})

    return render(request, 'main_page/main_content.html', {
        'league_data': league_id_2_name,
        'stat_facts': stats_facts,
        'tournament_table': table_tournament,
        'team_emblems': team_emblems
    })


@csrf_exempt
def last_games(request, pk=None):
    _filter = {'date__gte': helpers.get_date_start_season(), 'team_home__active': True, 'team_away__active': True,
               'league__id': pk}
    plays = list(
        Play.objects.select_related('team_home', 'team_away', 'league').order_by('-date').filter(**_filter)[:10])
    return render(request, 'main_page/last_games_table.html', {'data_table': plays})
