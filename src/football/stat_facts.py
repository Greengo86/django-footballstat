from operator import itemgetter

stat_fields = {
    'Удары по воротам': 'shot_on_goal',
    'Удары в створ': 'shot_on_target',
    'Фолы': 'fouls',
    'Угловые': "corners",
    'Офсайды': 'offsides',
    '% владения мячом': 'possession',
    'Заблокированные удары': 'blocked_shots',
    'Штрафные удары': 'free_shots',
    'Предупреждения': 'yellow_cards',
    'Удаления': 'red_cards',
}


def get_factory():
    def get_stat_facts(plays: list) -> dict:
        result_dict, team_emblem = {}, {}
        for play in plays:
            main_stat = ['total_score', 'score_home', 'score_away', 'missed_goals', 'played_games']
            stats_list = list(stat_fields.values())
            stats_list.extend(main_stat)
            for stat_element in stats_list:
                if stat_element not in result_dict:
                    result_dict[stat_element] = {}
                    result_dict[stat_element].update({play.team_home.name: 0})
                    result_dict[stat_element].update({play.team_away.name: 0})
                if play.team_home.name not in result_dict[stat_element]:
                    result_dict[stat_element].update({play.team_home.name: 0})
                if play.team_away.name not in result_dict[stat_element]:
                    result_dict[stat_element].update({play.team_away.name: 0})

                if stat_element in main_stat:
                    if stat_element == 'played_games':
                        result_dict['played_games'][play.team_home.name] += 1
                        result_dict['played_games'][play.team_away.name] += 1
                    if stat_element == 'score_home':
                        result_dict['score_home'][play.team_home.name] += int(getattr(play, 'score_home', 0))
                        result_dict['total_score'][play.team_home.name] += int(getattr(play, 'score_home', 0))
                    if stat_element == 'score_away':
                        result_dict['score_away'][play.team_away.name] += int(getattr(play, 'score_away', 0))
                        result_dict['total_score'][play.team_away.name] += int(getattr(play, 'score_away', 0))
                    if stat_element == 'missed_goals':
                        result_dict['missed_goals'][play.team_home.name] += int(getattr(play, 'score_away', 0))
                        result_dict['missed_goals'][play.team_away.name] += int(getattr(play, 'score_home', 0))
                else:
                    result_dict[stat_element][play.team_home.name] += int(getattr(play, 'home_' + stat_element, 0))
                    result_dict[stat_element][play.team_away.name] += int(getattr(play, 'away_' + stat_element, 0))

            # Пока не нужны эмблемы - генерю их на уровень выше!
            # if play.team_home.name not in team_emblem:
            #     team_emblem.update({play.team_home.name: play.team_home.emblem})
            # if play.team_away.name not in team_emblem:
            #     team_emblem.update({play.team_away.name: play.team_away.emblem})

        average_stat_fields = get_average_stat_fields(result_dict)
        stats_facts = {}
        for stat_element in filter(lambda n: n != 'played_games', average_stat_fields.keys()):
            stats_facts.update({stat_element: max(average_stat_fields[stat_element].items(), key=itemgetter(1))})
        return stats_facts

    return get_stat_facts


def get_average_stat_fields(result_dict: dict) -> dict:
    for stat_element, data in result_dict.items():
        if stat_element != 'played_games':
            for team, score in data.items():
                result_dict[stat_element][team] = score / result_dict['played_games'][team]
    return result_dict
