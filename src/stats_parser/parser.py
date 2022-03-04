import os
import asyncio

from stats_parser.parse_extractor import TeamsPageExtractor, UrlChampPageExtractor, StatExtractor, async_prepare_soup
from football.models import League, Team, Play
from stats_parser.json_provider import JSONProvider
from football.helpers import time_track
from asgiref.sync import sync_to_async


os.environ['PYTHONASYNCIODEBUG'] = '1'


async def get_pages(extractor: type, parse_type: str) -> list:
    json_provider = JSONProvider()
    total_sources = json_provider.get('sources')

    sources = total_sources.get(parse_type).items()

    league_soups_tasks = [asyncio.create_task(async_prepare_soup(source)) for league, source in sources]
    soup_league = await asyncio.gather(*league_soups_tasks)

    source_2_league_map = {source: league for league, source in sources}

    pages = [extractor(source=source, soup=soup, league=source_2_league_map[source]) for soup, source in soup_league]
    return pages


class ParseType:
    @staticmethod
    async def teams(parse_type: str) -> None:
        # Выполняем Парсинг команд со страницы последних матчей
        team_pages = await get_pages(extractor=TeamsPageExtractor, parse_type=parse_type)
        for page in team_pages:
            teams_data = await page()
            if teams_data:
                await save_teams(league=page.league, data_teams_dict=teams_data)
            else:
                print('Новых Команд не нашли ((')

    @staticmethod
    async def last_plays(parse_type: str) -> None:
        await plays(parse_type)

    @staticmethod
    async def all_plays(parse_type: str) -> None:
        await plays(parse_type)


async def plays(parse_type: str) -> None:
    # Парсинг страницы с результатами конкретных матчей и статы в них
    pages = await get_pages(extractor=UrlChampPageExtractor, parse_type=parse_type)
    urls_tasks = [asyncio.create_task(page.get_urls(type_parse=parse_type)) for page in pages]
    await asyncio.gather(*urls_tasks)

    stat_tasks = []

    # Здесь придут ссылки на матчи, которых нет в бд, но завершились они не все!
    for page in pages:
        for url, soup in page.url_2_soup:
            stat_tasks.append(asyncio.create_task(StatExtractor(source=url, soup=soup, league=page.league).process_parse()))

    if stat_tasks:
        result_stat_tasks = await asyncio.gather(*stat_tasks)
        for result_dict in result_stat_tasks:
            if not result_dict:
                # А вот здесь проверим закончился ли матч и если пришел None, то матч не Окончен -  Запишем это в лог
                print("Match is not beginning or not started")
            else:
                # Если игру не нашли в базе запишем её. На этом этапе уже знаем, что ее мы ещё не записывали
                await sync_to_async(Play.objects.create, thread_sensitive=True)(**result_dict)
    else:
        print('Plays for insert in db not found. Finishing')


async def save_teams(league: str, data_teams_dict: dict):
    # В сезоне 13/14 был Интер теперь Интер М! Не забыть переименовать - сейчас Интер М в базе
    league_object = await sync_to_async(League.objects.get, thread_sensitive=True)(name=league)
    teams_in_db = await sync_to_async(Team.objects.filter, thread_sensitive=True)(league=league_object.id)
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

        sync_to_async(team.save(), thread_sensitive=True)

    # А здесь остались новые команды, которых никогда не было в бд - создадим их
    for team_name, data in data_teams_dict.items():
        new_team = Team()
        new_team.emblem = data['emblem']
        new_team.league = league_object
        new_team.name = team_name
        new_team.tag_href = data['tag_href_team']
        new_team.stadium = data['stadium']
        new_team.head_coach = data['head_coach']
        sync_to_async(new_team.save(), thread_sensitive=True)


class CustomParse(object):
    def __init__(self, type_parser: str):
        self.type_parser = type_parser

    def switch(self) -> None:
        # m = getattr(self, 'parse_{}'.format(case), None)
        f = getattr(ParseType, self.type_parser, None)
        if not f:
            return self.default()

        # go
        return asyncio.run(f(self.type_parser))

    __call__ = switch

    def default(self):
        raise Exception('Type parse not found!')


@time_track
def main(type_parser: str):
    '''
    58-60 секунд работает в синхронном режиме - teams()
    17 секунд в асинхронном режиме (после рефакторинга 9.2), а иногда и 104 секунды в синх.  last_plays()
    2350, секунд работает в синхронном режиме! 215 секунд в асинхронном режиме all_plays()
    '''
    parse_way = CustomParse(type_parser)
    parse_way()


# running for manual tests
if __name__ == '__main__':
    main('all_plays')
