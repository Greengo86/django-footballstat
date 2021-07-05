import os
from datetime import datetime
from urllib.parse import urljoin
from json_provider import JSONProvider

import django
import requests
from bs4 import BeautifulSoup
from footballstat.settings import BASE_DOMEN

os.environ['DJANGO_SETTINGS_MODULE'] = 'footballstat.settings'
django.setup()

from football.models import League, Team

stats = {
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


class FootballParser():

    def __init__(self, source, type_config):
        self.source = source
        self.json_provider = JSONProvider()
        self.class_config = self.get_config_by_type(type_config=type_config)
        response = requests.get(url=self.source, headers=self.json_provider.get('headers'))
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def get_config_by_type(self, type_config):
        return self.json_provider.get(type_config)

    def custom_find_elements(self, element, dom_params):
        return self.soup.findAll(element, dom_params)

    def custom_find_element(self, element, dom_params):
        return self.soup.find(element, dom_params)


class UrlChampPageExtractor(FootballParser):
    type_config = 'url_champ_page'

    def __init__(self, source, league):
        super().__init__(source, self.type_config)
        self.urls = []
        self.league = league

    def get_urls(self, type):
        if type == 'all_plays':
            # div всего чемпионата - таблица всех матчей - 380 игр! Собираем ссылки на все игры отдельного чемпа
            div_full_tournament_tab = self.custom_find_elements(self.class_config['divs_with_stats_results']['tag'],
                                                                {"class": self.class_config['divs_with_stats_results'][
                                                                    'class']})

            [self.urls.append(item.contents[1].get('href')) for item in div_full_tournament_tab]
        elif type == 'last_plays':
            # div последних матчей чемпионата - всего 10!
            div_tournament_tabs = self.custom_find_elements(element=self.class_config['urls_page']['tag'],
                                                            dom_params=self.class_config['urls_page']['class'])
            # Здесь фильтруем закончившиеся матчи, отбрасывая будущие
            div = [div_url for div_url in div_tournament_tabs if div_url.get('data-type') == 'next'][0]
            div_with_urls = div.findAll(self.class_config['divs_with_stats_results']['tag'],
                                        {"class": self.class_config['divs_with_stats_results']['class']})
            for item in div_with_urls:
                [self.urls.append(info.get('href')) for info in item.contents]
        else:
            raise Exception('Type plays parse not found!')


class StatExtractor(FootballParser):
    type_config = 'stat'

    def __init__(self, source):
        super().__init__(urljoin(BASE_DOMEN, source), self.type_config)

    def handle_parse(self, league):
        # Решил передавать league от UrlChampPageExtractor
        result_dict = {'url': self.source, 'league': League.objects.get(name=league)}
        status_stub = self.custom_find_element(
            element=self.class_config['status_dom']['tag'],
            dom_params=self.class_config['status_dom']['class'])
        if status_stub.text.strip() != 'Окончен':
            return
        else:
            date_div = self.custom_find_element(
                element=self.class_config['date_dom']['tag'],
                dom_params=self.class_config['date_dom']['class'])
            result_dict['date'] = self.refine_date(date_div.text.strip())
            link_team_div = self.custom_find_elements(
                element=self.class_config['link_team_dom']['tag'],
                dom_params=self.class_config['link_team_dom']['class'])
            tag_home = HrefAboutTeam(source=link_team_div[0].get('href')).find_team_tag()
            tag_away = HrefAboutTeam(source=link_team_div[1].get('href')).find_team_tag()

            result_dict['team_home'] = Team.objects.filter(**{'active': True, 'tag_href': tag_home}).first()
            result_dict['team_away'] = Team.objects.filter(**{'active': True, 'tag_href': tag_away}).first()

            if not result_dict['team_home'] or not result_dict['team_away']:
                # Если не нашли команду по тегам попробуем найти по имени команды
                teams_div = self.custom_find_elements(
                    element=self.class_config['teams_dom']['tag'],
                    dom_params=self.class_config['teams_dom']['class'])
                if not result_dict['team_home']:
                    team_home_name = teams_div[0].text.strip()
                    result_dict['team_home'] = Team.objects.filter(**{'active': True, 'name': team_home_name}).first()
                if not result_dict['team_away']:
                    team_away_name = teams_div[1].text.strip()
                    result_dict['team_away'] = Team.objects.filter(**{'active': True, 'name': team_away_name}).first()

            score_div = self.custom_find_element(
                element=self.class_config['score_dom']['tag'],
                dom_params=self.class_config['score_dom']['class'])
            result_dict['score_home'], result_dict['score_away'] = score_div.text.strip().split(':')[0], \
                                                                   score_div.text.strip().split(':')[1]
            div = self.custom_find_elements(
                element=self.class_config['stat_graph']['tag'],
                dom_params=self.class_config['stat_graph']['class'])
            stats_divs = div[1].findChildren()
            for item in stats_divs:
                if item.get('class')[0] == 'stat-graph__row':
                    row = item.text.strip().split('\n')
                    if row[1] in stats.keys():
                        result_dict['home_' + stats[row[1]]], result_dict['away_' + stats[row[1]]] = row[0].strip(), \
                                                                                                     row[2].strip()
            return result_dict

    def refine_date(self, string):
        a = string.split(',')
        date_stub = a[0] + ' ' + a[1].split()[1]

        date_str = self.int_value_from_ru_month(date_stub)
        return datetime.strptime(date_str, '%d %m %Y %H:%M')

    def int_value_from_ru_month(self, date_stub):
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

    def __init__(self, source, league):
        super().__init__(source, self.type_config)
        self.league = league

    def get_teams(self):
        # Найдем div c командами
        div_tournament_tabs = self.custom_find_elements(element=self.class_config['tournament_tabs']['tag'],
                                                        dom_params=self.class_config['tournament_tabs']['class'])
        # А теперь отфильтруем и возьмём ссылки на команды только из турнирной таблицы
        for table_div in div_tournament_tabs:
            if table_div.get('data-type') == 'table':
                teams_div = table_div.findAll(self.class_config['teams']['tag'], self.class_config['teams']['class'])
                break

        teams = {}
        league_object = League.objects.get(name=self.league)

        for team_div in teams_div:
            # Найдем ссылку на страницу команды профиля команды - '/tags/...' и по ней и будем идентифицировать команду
            href_about_team = HrefAboutTeam(source=team_div.get('href')).find_team_tag()
            # А теперь найдём на странице профиля найдём всю инфу о ней
            # У некоторых команд в Италии и Германии почему-то нет ссылок - ну как так то Пацаны(((
            # HrefAboutTeam(source=href_about_team).find_info_team_by_tag()- до этого так парсил данные со странице
            # о команде. Оказыввется она есть не у всех. Теперь парсим со странице с результами команды
            team_info = HrefAboutTeam(source=team_div.get('href')).find_info_team_by_tag()

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

    def __init__(self, source):
        super().__init__(urljoin(BASE_DOMEN, source), self.type_config)

    def find_team_tag(self):
        team_div_tag_element = self.custom_find_element(
            element=self.class_config['href_team_div']['tag'],
            dom_params=self.class_config['href_team_div']['class']
        )

        return team_div_tag_element.findChildren()[1]['href'] if team_div_tag_element else None

    def find_info_team_by_tag(self):
        header_image = self.custom_find_element(element=self.class_config['header_image']['tag'],
                                                dom_params=self.class_config['header_image']['class']).contents[1]
        header_facts = self.custom_find_element(element=self.class_config['header_facts']['tag'],
                                                dom_params=self.class_config['header_facts']['class'])

        # Old вариант парсинга со странице "О команде" - href_about_team оказывается эта страница есть не у всех команд(
        # {'emblem': header_image.get('src'),
        #  'name': header_image.get('alt'),
        #  'coach': coach_stub[2].strip(),
        #  'stadium': header_facts.contents[7].text.split('\n')[2].strip() if len(header_facts.contents) > 7
        #  else 'Нет Стадиона'}

        return {'emblem': header_image.contents[1].get('src'),
                'name': header_image.contents[1].get('alt'),
                'coach': header_facts.contents[5].text.split('\n')[2].strip() if len(header_facts.contents) > 5
                else header_facts.contents[3].text.split('\n')[2].strip(),
                'stadium': header_facts.contents[3].text.split('\n')[2].strip() if len(header_facts.contents) > 5
                else 'Нет Стадиона'}
