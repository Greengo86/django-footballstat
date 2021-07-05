from football import repository
from operator import itemgetter

stats_dict = {
    'goals': {},
    'missed_goals': {},
    'shot_on_goal': {},
    'possesion': {},
    'fouls': {},
    'corners': {},
    'offside': {},
    'yellow_carts': {},
    'red_carts': {},
    'played_games': {},
}


def get_factory(league_id):
    def get_stat_facts(plays):
        {stats_dict[stat_element].update({team.name: 0}) for team in repository.get_teams(league_id) for
         stat_element in stats_dict.keys()}
        # for team in repository.get_teams(league_id):
        #     for stat_element in self.stats_dict.keys():
        #         self.stats_dict[stat_element].update({team.name: 0})
        team_emblem = {}
        for play in plays:
            # todo переделать поля в базе на названия ниже и обрабатывать инфу в цикле будет удобнее!!!
            # for stat_element in stats_dict.keys():
            #     if stat_element == 'missed_goals':
            #         stats_dict[stat_element][play.home_team.name] += int(play.away_score_full)
            #         stats_dict[stat_element][play.away_team.name] += int(play.home_score_full)
            #         continue
            #     if stat_element == 'played_games':
            #         stats_dict['played_games'][play.home_team.name] += 1
            #         stats_dict['played_games'][play.away_team.name] += 1
            #         continue
            stats_dict['goals'][play.home_team.name] += int(play.home_score_full)
            stats_dict['goals'][play.away_team.name] += int(play.away_score_full)
            stats_dict['missed_goals'][play.home_team.name] += int(play.away_score_full)
            stats_dict['missed_goals'][play.away_team.name] += int(play.home_score_full)
            stats_dict['shot_on_goal'][play.home_team.name] += int(play.h_tid_shot_on_goal)
            stats_dict['shot_on_goal'][play.away_team.name] += int(play.a_tid_shot_on_goal)
            stats_dict['possesion'][play.home_team.name] += int(play.h_tid_possesion)
            stats_dict['possesion'][play.away_team.name] += int(play.a_tid_possesion)
            stats_dict['fouls'][play.home_team.name] += int(play.h_tid_foul)
            stats_dict['fouls'][play.away_team.name] += int(play.a_tid_foul)
            stats_dict['corners'][play.home_team.name] += int(play.h_tid_corner)
            stats_dict['corners'][play.away_team.name] += int(play.a_tid_corner)
            stats_dict['offside'][play.home_team.name] += int(play.h_tid_offside)
            stats_dict['offside'][play.away_team.name] += int(play.a_tid_offside)
            stats_dict['yellow_carts'][play.home_team.name] += int(play.h_tid_yellow_cart)
            stats_dict['yellow_carts'][play.away_team.name] += int(play.a_tid_yellow_cart)
            stats_dict['red_carts'][play.home_team.name] += int(play.h_tid_red_cart)
            stats_dict['red_carts'][play.away_team.name] += int(play.a_tid_red_cart)
            stats_dict['played_games'][play.home_team.name] += 1
            stats_dict['played_games'][play.away_team.name] += 1
            if play.home_team.name not in team_emblem:
                team_emblem.update({play.home_team.name: play.home_team.emblem})
            if play.away_team.name not in team_emblem:
                team_emblem.update({play.away_team.name: play.away_team.emblem})
        average_stats_dict = get_average_stats_dict()
        stats_facts = {}
        for stat_element in filter(lambda n: n != 'played_games', average_stats_dict.keys()):
            stats_facts.update({stat_element: max(average_stats_dict[stat_element].items(), key=itemgetter(1))})
        return stats_facts

    return get_stat_facts


def get_average_stats_dict():
    for stat_element, data in stats_dict.items():
        if stat_element != 'played_games':
            for team, score in data.items():
                stats_dict[stat_element][team] = score / stats_dict['played_games'][team]
    return stats_dict
