from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from football.models import League, Play, Team
from . import stat_facts, tournament_table
from football import repository


def main(request):
    stats_facts, table_tournament, league_ids = {}, {}, {}
    # league_ids = {league.id: league.name for league in League.objects.all()}
    # stats_factories = [stat_facts.get_factory(league_id) for league_id in league_ids]
    # for league in League.objects.all():
    #     league_ids.update({league.id: league.name})
    #     plays = repository.get_current_seasson_plays_by_league(league.id, with_related='team')
    #     get_stats, get_table = stat_facts.get_factory(league.id), tournament_table.get_factory(league.id)
    #     stats_facts.update({league.name: get_stats(plays)})
    #     table_tournament.update({league.name: get_table(plays)})
    team_emblems = Team.objects.values_list('name', 'emblem')
    return render(request, 'main_page/main_content.html', {
        'league_data': league_ids,
        'stat_facts': stats_facts,
        'tournament_table': table_tournament,
        'team_emblems': team_emblems
    })


@csrf_exempt
def last_games(request, pk=None):
    play_data = []
    for play in Play.objects.filter(league__id=pk).order_by('-date')[:10]:
        play_data.append(play)
    return render(request, 'main_page/last_games_table.html', {'data_table': play_data})

    # our_tz = pytz.timezone('Europe/Moscow')
    # ww = datetime.datetime.now()
    # qq = datetime.datetime.utcnow()
    # ee = datetime.datetime(2017, 7, 30)
    # tt = datetime.datetime(2017, 7, 30, tzinfo=our_tz)
    # print(f'default dt - {ee}')
    # print(f'our tz dt - {tt}')
    # datetime1 = datetime.datetime(2017, 7, 30)
