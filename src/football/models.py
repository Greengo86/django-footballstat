from datetime import datetime

from django.core.validators import URLValidator
from django.db import models


class League(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название лиги',
                            unique=True)

    emblem = models.CharField(default=None,
                              max_length=170,
                              verbose_name='Эмблема')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Лига Европейских чемпионатов'
        verbose_name_plural = 'Лиги Европейских чемпионатов'

    def __str__(self):
        return self.name


class Play(models.Model):
    url = models.URLField(max_length=180,
                          verbose_name='Ссылка на игру',
                          unique=True,
                          validators=[URLValidator])

    date = models.DateTimeField()

    league = models.ForeignKey('League', on_delete=models.CASCADE,
                               verbose_name='ID Лиги', related_name='play_to_league')

    team_home = models.ForeignKey('Team', on_delete=models.CASCADE,
                                  verbose_name='ID Команды хозяев', related_name='plays_home_to_team')

    team_away = models.ForeignKey('Team', on_delete=models.CASCADE,
                                  verbose_name='ID гостевой Команды', related_name='plays_away_to_team')

    score_home = models.CharField(max_length=10, verbose_name='Голы Хозяев')

    score_away = models.CharField(max_length=10, verbose_name='Голы Гостей')

    home_possession = models.CharField(max_length=10, verbose_name='Владение Хозяев')

    away_possession = models.CharField(max_length=10, verbose_name='Владение Гостей')

    home_shot_on_goal = models.CharField(max_length=10, verbose_name='Удары по воротам Хозяев')

    away_shot_on_goal = models.CharField(max_length=10, verbose_name='Удары по воротам Гостей')

    home_shot_on_target = models.CharField(max_length=10, verbose_name='Удары в створ Хозяев')

    away_shot_on_target = models.CharField(max_length=10, verbose_name='Удары в створ Гостей')

    home_blocked_shots = models.CharField(max_length=10, verbose_name='Блокированные удары Хозяев')

    away_blocked_shots = models.CharField(max_length=10, verbose_name='Блокированные удары Гостей')

    home_fouls = models.CharField(max_length=10, verbose_name='Фолы Хозяев')

    away_fouls = models.CharField(max_length=10, verbose_name='Фолы Гостей')

    home_free_shots = models.CharField(max_length=10, verbose_name='Штрафные удары Хозяев')

    away_free_shots = models.CharField(max_length=10, verbose_name='Штрафные удары Гостей')

    home_corners = models.CharField(max_length=10, verbose_name='Угловые Хозяев')

    away_corners = models.CharField(max_length=10, verbose_name='Угловые Гостей')

    home_offsides = models.CharField(max_length=10, verbose_name='Оффсайды Хозяев')

    away_offsides = models.CharField(max_length=10, verbose_name='Оффсайды Гостей')

    home_yellow_cards = models.CharField(max_length=10, verbose_name='Желтые Карточки Хозяев')

    away_yellow_cards = models.CharField(max_length=10, verbose_name='Желтые Карточки Гостей')

    home_red_cards = models.CharField(max_length=10, verbose_name='Красные Карточки Хозяев')

    away_red_cards = models.CharField(max_length=10, verbose_name='Красные Карточки Гостей')

    delay = models.BooleanField(default=False, verbose_name='Матч задержан')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'

    def __str__(self):
        return self.team_home.name + self.team_away.name + datetime.strftime(self.date, '%d %m %Y %H:%M')


class Team(models.Model):
    name = models.CharField(max_length=70,
                            verbose_name='Команда')

    emblem = models.CharField(max_length=170,
                              verbose_name='Эмблема')

    stadium = models.CharField(max_length=170,
                               verbose_name='Стадион')

    league = models.ForeignKey('League', on_delete=models.CASCADE,
                               verbose_name='ID Лиги', related_name='team_to_league')

    active = models.BooleanField(default=True,
                                 verbose_name='Команда не активна')

    tag_href = models.CharField(max_length=70,
                                verbose_name='Ccылка на страницу профиля команды',
                                unique=True)

    head_coach = models.CharField(max_length=70,
                                  verbose_name='Главный тренер команды')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Команды'
        verbose_name_plural = 'Команды'

    def __str__(self):
        return self.name
