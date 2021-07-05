from football import repository
from operator import itemgetter
from collections import OrderedDict, defaultdict

table_stat_item = ['games', 'points', 'goals', 'missed_goals']


def get_factory(league_id):
    def get_table(plays):
        team_stat = {team.name: {} for team in repository.get_teams(league_id)}
        for team in repository.get_teams(league_id):
            team_stat[team.name] = {}
            for item in table_stat_item:
                team_stat[team.name].update({item: 0})
        for play in plays:
            if play.home_score_full > play.away_score_full:
                team_stat[play.home_team.name]['points'] += 3
            elif play.home_score_full < play.away_score_full:
                team_stat[play.away_team.name]['points'] += 3
            else:
                team_stat[play.home_team.name]['points'] += 1
                team_stat[play.away_team.name]['points'] += 1
            team_stat[play.home_team.name]['games'] += 1
            team_stat[play.away_team.name]['games'] += 1
            team_stat[play.home_team.name]['goals'] += int(play.home_score_full)
            team_stat[play.away_team.name]['goals'] += int(play.away_score_full)
            team_stat[play.home_team.name]['missed_goals'] += int(play.away_score_full)
            team_stat[play.away_team.name]['missed_goals'] += int(play.home_score_full)
        table = OrderedDict(sorted(team_stat.items(), key=lambda x: x[1]['points'], reverse=True))
        result_table = {0: {}, 1: {}, 2: {}}
        for count, (stat_team, stats) in enumerate(table.items()):
            count += 1
            if count <= 8:
                result_table[0].update({stat_team: stats})
            elif 8 < count <= 16:
                result_table[1].update({stat_team: stats})
            elif count > 16:
                result_table[2].update({stat_team: stats})
        return result_table
    return get_table

