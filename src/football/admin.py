from django.contrib import admin
from django.contrib.admin import ModelAdmin
from football.models import *


class PlayAdmin(ModelAdmin):
    list_display = ['date', 'home_team', 'home_score_full', 'away_team', 'away_score_full', 'league', 'delay']
    list_filter = ['home_team', 'away_team', 'league']
    search_fields = ['home_team__name', 'away_team__name']
    fieldsets = (
        ('Дополнительная информация о игре', {
            'fields': ('date', 'league', 'delay')
        }),
        ('Основная информация о игре', {
            'fields': ('home_team', 'home_score_full', 'away_team', 'away_score_full')
        }),
        ('Статистика', {
            'fields': ('h_tid_possesion', 'a_tid_possesion', 'h_tid_shot_on_goal', 'a_tid_shot_on_goal', 'h_tid_foul',
                       'a_tid_foul', 'h_tid_corner', 'a_tid_corner', 'h_tid_offside', 'a_tid_offside', 'h_tid_yellow_cart',
                       'a_tid_yellow_cart', 'h_tid_red_cart', 'a_tid_red_cart'),
            'description': 'Разнообразная статистика',
            'classes': ['collapse']
        }),
    )

    actions = ['mark_as_delay']

    def mark_as_delay(self, request, queryset):
        queryset.update(delay=True)

    mark_as_delay.short_description = 'Перевести в статус Перенесено'


class TeamAdmin(ModelAdmin):
    list_display = ['name', 'stadium', 'league']


# admin.site.register(Play, PlayAdmin)
# admin.site.register(Team, TeamAdmin)
# admin.site.register(League)
