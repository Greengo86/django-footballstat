# Generated by Django 2.2.17 on 2021-05-06 21:38

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название лиги')),
                ('emblem', models.CharField(default=None, max_length=170, verbose_name='Эмблема')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Лига Европейских чемпионатов',
                'verbose_name_plural': 'Лиги Европейских чемпионатов',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70, verbose_name='Команда')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_to_league',
                                             to='football.League', verbose_name='ID Лиги')),
                ('emblem', models.CharField(max_length=170, verbose_name='Эмблема')),
                ('stadium', models.CharField(max_length=170, verbose_name='Стадион')),
                ('active', models.BooleanField(default=True, verbose_name='Команда не активна')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Команды',
                'verbose_name_plural': 'Команды',
            },
        ),
        migrations.CreateModel(
            name='Play',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=180, unique=True, validators=[django.core.validators.URLValidator],
                                        verbose_name='Ссылка на игру')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='play_to_league',
                                             to='football.League', verbose_name='ID Лиги')),
                ('team_away',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plays_away_to_team',
                                   to='football.Team', verbose_name='ID гостевой Команды')),
                ('team_home',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plays_home_to_team',
                                   to='football.Team', verbose_name='ID Команды хозяев')),
                ('date', models.DateTimeField()),
                ('score_home', models.CharField(max_length=10, verbose_name='Голы Хозяев')),
                ('score_away', models.CharField(max_length=10, verbose_name='Голы Гостей')),
                ('home_possession', models.CharField(max_length=10, verbose_name='Владение Хозяев')),
                ('away_possession', models.CharField(max_length=10, verbose_name='Владение Гостей')),
                ('home_shot_on_goal', models.CharField(max_length=10, verbose_name='Удары по воротам Хозяев')),
                ('away_shot_on_goal', models.CharField(max_length=10, verbose_name='Удары по воротам Гостей')),
                ('home_shot_on_target', models.CharField(max_length=10, verbose_name='Удары в створ Хозяев')),
                ('away_shot_on_target', models.CharField(max_length=10, verbose_name='Удары в створ Гостей')),
                ('home_blocked_shots', models.CharField(max_length=10, verbose_name='Блокированные удары Хозяев')),
                ('away_blocked_shots', models.CharField(max_length=10, verbose_name='Блокированные удары Гостей')),
                ('home_fouls', models.CharField(max_length=10, verbose_name='Фолы Хозяев')),
                ('away_fouls', models.CharField(max_length=10, verbose_name='Фолы Гостей')),
                ('home_free_shots', models.CharField(max_length=10, verbose_name='Штрафные удары Хозяев')),
                ('away_free_shots', models.CharField(max_length=10, verbose_name='Штрафные удары Гостей')),
                ('home_corners', models.CharField(max_length=10, verbose_name='Угловые Хозяев')),
                ('away_corners', models.CharField(max_length=10, verbose_name='Угловые Гостей')),
                ('home_offsides', models.CharField(max_length=10, verbose_name='Оффсайды Хозяев')),
                ('away_offsides', models.CharField(max_length=10, verbose_name='Оффсайды Гостей')),
                ('home_yellow_cards', models.CharField(max_length=10, verbose_name='Желтые Карточки Хозяев')),
                ('away_yellow_cards', models.CharField(max_length=10, verbose_name='Желтые Карточки Гостей')),
                ('home_red_cards', models.CharField(max_length=10, verbose_name='Красные Карточки Хозяев')),
                ('away_red_cards', models.CharField(max_length=10, verbose_name='Красные Карточки Гостей')),
                ('delay', models.BooleanField(default=False, verbose_name='Матч задержан')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Игра',
                'verbose_name_plural': 'Игры',
            },
        ),
    ]
