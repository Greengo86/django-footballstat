from parse_extractor import StatExtractor, UrlChampPageExtractor, TeamsPageExtractor
from football.models import League, Team, Play
from json_provider import JSONProvider
from football.helpers import time_track


@time_track
def main(type_parser):
    parse_way = CustomParse()
    parse_way(type_parser)

    # parse_roadway = {
    #     'parse_team': teams(),
    #     'parse_plays': plays(),
    # }.get(type_parser, parsing_void())


def teams(json_provider):
    sources = json_provider.get('sources').items()
    pages = [TeamsPageExtractor(source=source, league=league) for league, source in sources]
    for page in pages:
        teams_data = page.get_teams()
        save_teams(league=page.league, data_teams_dict=teams_data)


def plays(json_provider, type):
    # Парсинг страницы с результатами
    sources = json_provider.get('sources').items()
    pages = [UrlChampPageExtractor(source=source, league=league) for league, source in sources]
    [page.get_urls(type=type) for page in pages]

    # Парсинг конкретного матча и статы в нем
    for page in pages:
        for url in page.urls:
            stat_extractor = StatExtractor(source=url)
            result_dict = stat_extractor.handle_parse(page.league)
            play = Play.objects.filter(**{'url': result_dict['url']}).first()
            if play is None:
                Play.objects.create(**result_dict)


def save_teams(league, data_teams_dict):
    # В сезоне 13/14 был Интер теперь Интер М! Не забыть переименовать - сейчас Интер М в базе
    league_object = League.objects.get(name=league)
    teams_in_db = Team.objects.filter(league__name=league)
    for team in teams_in_db:
        if team.name not in data_teams_dict:
            team.active = False
        else:
            # Обновим инфу по эмблеме и по имени стадиона
            team.active = True
            team_data = data_teams_dict[team.name]
            team.emblem = team_data['emblem']
            team.tag_href = team_data['tag_href_team']
            team.stadium = team_data['stadium']
            team.head_coach = team_data['head_coach']
            # А теперь удалим эту команду, чтобы не создавать её далее вновь
            del (data_teams_dict[team.name])

        team.save()

    # А здесь остались новые команды, которых никогда не было в бд - создадим их
    for team_name, data in data_teams_dict.items():
        team_obj = Team()
        team_obj.emblem = data['emblem']
        team_obj.league = league_object
        team_obj.name = team_name
        team_obj.tag_href = data['tag_href_team']
        team_obj.stadium = data['stadium']
        team_obj.head_coach = data['head_coach']
        team_obj.save()


class ParseBaseType:
    def switch(self, case):
        m = getattr(self, 'parse_{}'.format(case), None)
        if not m:
            return self.default()
        return m()

    __call__ = switch


class CustomParse(ParseBaseType):
    json_provider = JSONProvider()

    # 58-60 секунд работает в синхронном режиме
    def parse_teams(self):
        return teams(CustomParse.json_provider)

    def parse_last_plays(self, loop):
        return plays(json_provider=CustomParse.json_provider, type='last_plays')

    # 2350 секунд работает в синхронном режиме
    def parse_all_plays(self, loop):
        return loop.run_until_complete(plays(json_provider=CustomParse.json_provider, type='all_plays'))

    def default(self):
        raise Exception('Type parse not found!')


if __name__ == '__main__':
    main('all_plays')

# конфиг с ссылками ближайщих матчей
# "Испания": "https://www.championat.com/football/_spain.html",
# "Италия": "https://www.championat.com/football/_italy.html",
# "Германия": "https://www.championat.com/football/_germany.html",
# "Англия": "https://www.championat.com/football/_england.html"