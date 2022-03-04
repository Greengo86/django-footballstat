from django.contrib import admin
from django.contrib.admin import ModelAdmin
from football.models import *


class PlayAdmin(ModelAdmin):
    list_display = ['date', 'team_home', 'score_home', 'team_away', 'score_away', 'league', 'delay']
    list_filter = ['team_home', 'team_away', 'league']
    search_fields = ['team_home__name', 'team_away__name']
    ordering = ['date']
    fieldsets = (
        ('Дополнительная информация о игре', {
            'fields': ('date', 'league', 'delay')
        }),
        ('Основная информация о игре', {
            'fields': ('team_home', 'score_home', 'team_away', 'score_away')
        }),
        ('Статистика', {
            'fields': ('home_possession', 'away_possession', 'home_fouls', 'away_fouls', 'home_shot_on_goal',
                       'away_shot_on_goal', 'home_shot_on_target', 'away_shot_on_target',
                       'home_blocked_shots', 'away_blocked_shots', 'home_corners', 'away_corners',
                       'home_offsides', 'away_offsides', 'home_free_shots', 'away_free_shots',
                       'home_yellow_cards', 'away_yellow_cards', 'home_red_cards', 'away_red_cards'),
            'description': 'Полная статистика матча',
            'classes': ['collapse']
        }),
    )

    actions = ['mark_as_delay']

    def mark_as_delay(self, request, queryset):
        queryset.update(delay=True)

    mark_as_delay.short_description = 'Перевести в статус Перенесено'


class TeamAdmin(ModelAdmin):
    list_display = ['name', 'stadium', 'active', 'stadium', 'head_coach', 'tag_href', 'league']
    search_fields = ['name', 'league']
    ordering = ['league']
    actions = ['mark_as_not_active']

    def mark_as_not_active(self, request, queryset):
        queryset.update(active=False)

    mark_as_not_active.short_description = 'Выставить команде НЕактивный статус'


admin.site.register(Play, PlayAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(League)
