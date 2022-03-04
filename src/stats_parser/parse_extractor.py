import asyncio
import os
from datetime import datetime
from typing import Optional, Any, Union
from urllib.parse import urljoin
from stats_parser.json_provider import JSONProvider
from asgiref.sync import sync_to_async
from pytz import timezone
from django.conf import settings

import django
import aiohttp
from bs4 import BeautifulSoup
from footballstat.settings import BASE_PARSING_DOMEN

os.environ['DJANGO_SETTINGS_MODULE'] = 'footballstat.settings'
django.setup()

from football.models import League, Play, Team
from football.stat_facts import stat_fields


async def async_prepare_soup(source: str) -> tuple[BeautifulSoup, Any]:
    json_provider = JSONProvider()
    # Заюзаем цикл True так как падает с - aiohttp.client_exceptions.ServerDisconnectedError: Server disconnected
    while True:
        try:
            async with aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(force_close=True, verify_ssl=False)) as session:
                async with session.get(source, headers=json_provider.get('headers')) as response:
                    print(f'Пошел парсить - {source}')
                    response_result = await response.read()
                    return BeautifulSoup(response_result, 'html.parser'), source
        except aiohttp.ClientConnectionError:
            print("Oops - ClientConnectionError - the connection was dropped before we finished")


class FootballParser:

    def __init__(self, source: str, soup: BeautifulSoup, type_config: str):
        self.source = source
        self.json_provider = JSONProvider()
        self.soup = soup
        self.class_config = self.get_config_by_type(type_config=type_config)

    def get_config_by_type(self, type_config: str):
        return self.json_provider.get(type_config)

    def custom_find_elements(self, element: str, dom_params: dict):
        return self.soup.findAll(element, dom_params)

    def custom_find_element(self, element: str, dom_params: dict):
        return self.soup.find(element, dom_params)


class UrlChampPageExtractor(FootballParser):
    """
    Класс, который принимает ссылку на лигу и парсит матчи, которые еще не записали в бд по типу - last_plays -
    матчи последних выходных, all_plays - матчи всего сезона. Может принимать source на чемпионаты,
    которые закончились несколько лет назад
    """
    type_config = 'url_champ_page'

    def __init__(self, source: str, soup: BeautifulSoup, league: str):
        super().__init__(source, soup, UrlChampPageExtractor.type_config)
        self.urls = []
        self.url_2_soup = []
        self.league = league

    async def get_urls(self, type_parse: str):
        temp_urls = []

        if type_parse == 'all_plays':
            # div всего чемпионата - таблица всех матчей - 380 игр! Собираем ссылки на все игры отдельного чемпа
            div_full_tournament_tab = self.custom_find_elements(self.class_config['divs_with_stats_results']['tag'],
                                                                {"class": self.class_config['divs_with_stats_results'][
                                                                    'class']})

            [temp_urls.append(urljoin(BASE_PARSING_DOMEN, item.contents[1].get('href'))) for item in
             div_full_tournament_tab]
        elif type_parse == 'last_plays':
            # div последних матчей чемпионата - всего 10!
            div_tournament_tabs = self.custom_find_elements(element=self.class_config['urls_page']['tag'],
                                                            dom_params=self.class_config['urls_page']['class'])
            # Здесь фильтруем закончившиеся матчи, отбрасывая будущие
            div = [div_url for div_url in div_tournament_tabs if div_url.get('data-type') == 'last'][0]
            div_with_urls = div.findAll(self.class_config['divs_with_stats_results']['tag'],
                                        {"class": self.class_config['divs_with_stats_results']['class']})

            for item in div_with_urls:
                [temp_urls.append(urljoin(BASE_PARSING_DOMEN, info.get('href'))) for info in item.contents]

        else:
            raise Exception('Type plays parse not found!')

        # Только если нет в базе такой игры записываем в свойство и дальше работаем с ссылкой на матч
        for url in temp_urls:
            play = await sync_to_async(Play.objects.filter, thread_sensitive=True)(url=url)
            if not play:
                self.urls.append(url)

        url_tasks = [asyncio.create_task(async_prepare_soup(source=url)) for url in self.urls]
        soups = await asyncio.gather(*url_tasks)
        self.url_2_soup = [[u, s] for s, u in soups]


class StatExtractor(FootballParser):
    type_config = 'stat'

    def __init__(self, source: str, soup: BeautifulSoup, league: str):
        super().__init__(source, soup, StatExtractor.type_config)
        self.league = league

    async def process_parse(self) -> Optional[dict[Union[str, Any], Union[int, Any]]]:
        # Сначало определим окончен ли матч или нет! Если нет сразу выходим
        status_stub = self.custom_find_element(
            element=self.class_config['status_dom']['tag'],
            dom_params=self.class_config['status_dom']['class'])

        if status_stub is None or status_stub.get_text(strip=True) != 'Окончен':
            return None
        else:
            # В result_dict по умолчанию записываю 0 во все стат показатели. Так как если их матче не будет инфы на
            # страничке с статистическими данными тоже не будет!
            # result_dict = defaultdict(lambda: 0)
            result_dict = {'url': self.source,
                           'league': await sync_to_async(League.objects.get, thread_sensitive=True)(name=self.league)}
            for stat_field in stat_fields.values():
                result_dict['home_' + stat_field] = 0
                result_dict['away_' + stat_field] = 0

            date_div = self.custom_find_element(
                element=self.class_config['date_dom']['tag'],
                dom_params=self.class_config['date_dom']['class'])
            result_dict['date'] = StatExtractor.refine_date(date_div.get_text(strip=True))
            link_team_div = self.custom_find_elements(
                element=self.class_config['link_team_dom']['tag'],
                dom_params=self.class_config['link_team_dom']['class'])

            home_href_about_team_url, away_href_about_team_url = urljoin(BASE_PARSING_DOMEN,
                                                                         link_team_div[0].get('href')), \
                                                                 urljoin(BASE_PARSING_DOMEN,
                                                                         link_team_div[1].get('href'))

            hrefs_tasks = [asyncio.create_task(async_prepare_soup(home_href_about_team_url)),
                           asyncio.create_task(async_prepare_soup(away_href_about_team_url))]

            soup_urls = await asyncio.gather(*hrefs_tasks)

            tag_home_tasks = []
            for item in soup_urls:
                tag_home_tasks.append(HrefAboutTeam(source=item[1], soup=item[0]).find_team_tag())

            tags = await asyncio.gather(*tag_home_tasks)
            team_tag_home, team_tag_away = tags[0], tags[1]

            if not team_tag_home or not team_tag_away:
                # Если не нашли команду по тегам попробуем найти по имени команды
                teams_div = self.custom_find_elements(
                    element=self.class_config['teams_dom']['tag'],
                    dom_params=self.class_config['teams_dom']['class'])
            if team_tag_home:
                result_dict['team_home'] = await sync_to_async(Team.objects.get, thread_sensitive=True)(
                    tag_href=team_tag_home,
                    active=True)
            else:
                team_home_name = teams_div[0].text.strip()
                result_dict['team_home'] = await sync_to_async(Team.objects.get, thread_sensitive=True) \
                    (name=team_home_name, active=True)

            if team_tag_away:
                result_dict['team_away'] = await sync_to_async(Team.objects.get, thread_sensitive=True)(
                    tag_href=team_tag_away,
                    active=True)
            else:
                team_away_name = teams_div[1].text.strip()
                result_dict['team_away'] = await sync_to_async(Team.objects.get, thread_sensitive=True) \
                    (name=team_away_name, active=True)

            score_div = self.custom_find_element(
                element=self.class_config['score_dom']['tag'],
                dom_params=self.class_config['score_dom']['class'])

            # почему-то strip в аргументе get_text() не хватает.Чтобы было только число в конце еще раз обрабатываю strip()
            result_dict['score_home'], result_dict['score_away'] = score_div.get_text(strip=True).split(':')[0].strip(), \
                                                                   score_div.get_text(strip=True).split(':')[1].strip()

            div = self.custom_find_elements(
                element=self.class_config['stat_graph']['tag'],
                dom_params=self.class_config['stat_graph']['class'])
            # Какого то х.. div может быть разного размера (((
            stats_divs = div[1].findChildren() if len(div) > 1 else div[0].findChildren()

            for item in stats_divs:
                if item.get('class')[0] == 'stat-graph__row':
                    row = item.get_text().strip().split('\n')
                    if row[1] in stat_fields.keys():
                        result_dict['home_' + stat_fields[row[1]]], result_dict['away_' + stat_fields[row[1]]] = \
                            row[0].strip(), row[2].strip()
            return result_dict

    @staticmethod
    def refine_date(string: str) -> datetime:
        a = string.split(',')
        date_stub = a[0] + ' ' + a[1].split()[1]

        date_str = StatExtractor.int_value_from_ru_month(date_stub)
        play_datetime = datetime.strptime(date_str, '%d %m %Y %H:%M')
        current_settings_time_zone = timezone(settings.TIME_ZONE)
        return current_settings_time_zone.localize(play_datetime)

    @staticmethod
    def int_value_from_ru_month(date_stub: str) -> str:
        ru_month_values = (
            ('января', 1),
            ('февраля', 2),
            ('марта', 3),
            ('апреля', 4),
            ('мая', 5),
            ('июня', 6),
            ('июля', 7),
            ('августа', 8),
            ('сентября', 9),
            ('октября', 10),
            ('ноября', 11),
            ('декабря', 12)
        )

        for k, v in ru_month_values:
            if k in date_stub:
                return date_stub.replace(k, str(v))


class TeamsPageExtractor(FootballParser):
    type_config = 'team_page'

    def __init__(self, source: str, soup: BeautifulSoup, league: str):
        super().__init__(source, soup, TeamsPageExtractor.type_config)
        self.league = league

    async def __call__(self) -> dict:
        # Найдем div c командами
        div_tournament_tabs = self.custom_find_elements(element=self.class_config['tournament_tabs']['tag'],
                                                        dom_params=self.class_config['tournament_tabs']['class'])
        # А теперь отфильтруем и возьмём ссылки на команды только из турнирной таблицы
        for table_div in div_tournament_tabs:
            if table_div.get('data-type') == 'table':
                teams_div = table_div.findAll(self.class_config['teams']['tag'], self.class_config['teams']['class'])
                break

        teams = {}
        league_object = await sync_to_async(League.objects.get, thread_sensitive=True)(name=self.league)

        for team_href in teams_div:
            # Найдем ссылку на страницу команды профиля команды - '/tags/...' и по ней и будем идентифицировать команду
            href_soup = asyncio.create_task(async_prepare_soup(urljoin(BASE_PARSING_DOMEN, team_href.get('href'))))

            soup_and_href = await href_soup
            teams_info_tasks = [
                asyncio.create_task(HrefAboutTeam(source=soup_and_href[1], soup=soup_and_href[0]).find_team_tag()),
                asyncio.create_task(
                    HrefAboutTeam(source=soup_and_href[1], soup=soup_and_href[0]).find_info_team_by_tag())]

            teams_info = await asyncio.gather(*teams_info_tasks)
            # href_about_team = HrefAboutTeam(source=team_div.get('href')).find_team_tag()
            # А теперь найдём на странице профиля найдём всю инфу о ней
            # У некоторых команд в Италии и Германии почему-то нет ссылок - ну как так то Пацаны(((
            # HrefAboutTeam(source=href_about_team).find_info_team_by_tag()- до этого так парсил данные со странице
            # о команде. Оказыввется она есть не у всех. Теперь парсим со странице с результами команды
            href_about_team, team_info = teams_info[0], teams_info[1]

            if team_info['name'] not in teams:
                teams[team_info['name']] = {
                    'emblem': team_info['emblem'],
                    'name': team_info['name'],
                    'league': league_object.id,
                    'stadium': team_info['stadium'],
                    'head_coach': team_info['coach'],
                    # Если нет ссылки-href_about_team просто запишем строку /tags/{имя команды}/ так как на это поле
                    # навешен флаг unique в базе
                    'tag_href_team': href_about_team if href_about_team else '/tags/' + team_info['name'] + '/',
                }
        return teams


class HrefAboutTeam(FootballParser):
    type_config = 'href_about'

    def __init__(self, source: str, soup: BeautifulSoup):
        super().__init__(source, soup, HrefAboutTeam.type_config)

    async def find_team_tag(self) -> Union[str, None]:
        team_div_tag_element = self.custom_find_element(
            element=self.class_config['href_team_div']['tag'],
            dom_params=self.class_config['href_team_div']['class']
        )

        return team_div_tag_element.findChildren()[1]['href'] if team_div_tag_element else None

    async def find_info_team_by_tag(self) -> dict:
        header_image = self.custom_find_element(element=self.class_config['header_image']['tag'],
                                                dom_params=self.class_config['header_image']['class']).contents[1]
        header_facts = self.custom_find_element(element=self.class_config['header_facts']['tag'],
                                                dom_params=self.class_config['header_facts']['class'])

        return {'emblem': header_image.contents[1].get('src'),
                'name': header_image.contents[1].get('alt'),
                'coach': header_facts.contents[5].get_text().split('\n')[2].strip() if len(header_facts.contents) > 5
                else header_facts.contents[3].get_text().split('\n')[2].strip(),
                'stadium': header_facts.contents[3].get_text().split('\n')[2].strip() if len(header_facts.contents) > 5
                else 'Нет Стадиона'}
