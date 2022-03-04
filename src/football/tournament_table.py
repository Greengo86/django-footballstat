from collections import OrderedDict


def get_factory():
    def get_table(plays: list) -> dict:
        team_stat = {}
        for play in plays:
            if play.team_home.name not in team_stat:
                team_stat[play.team_home.name] = {'points': 0, 'games': 0, 'goals': 0, 'missed_goals': 0}
            if play.team_away.name not in team_stat:
                team_stat[play.team_away.name] = {'points': 0, 'games': 0, 'goals': 0, 'missed_goals': 0}

            if int(play.score_home) > int(play.score_away):
                team_stat[play.team_home.name]['points'] += 3
            elif int(play.score_home) < int(play.score_away):
                team_stat[play.team_away.name]['points'] += 3
            else:
                team_stat[play.team_home.name]['points'] += 1
                team_stat[play.team_away.name]['points'] += 1

            team_stat[play.team_home.name]['games'] += 1
            team_stat[play.team_away.name]['games'] += 1
            team_stat[play.team_home.name]['goals'] += int(play.score_home)
            team_stat[play.team_away.name]['goals'] += int(play.score_away)
            team_stat[play.team_home.name]['missed_goals'] += int(play.score_away)
            team_stat[play.team_away.name]['missed_goals'] += int(play.score_home)
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

