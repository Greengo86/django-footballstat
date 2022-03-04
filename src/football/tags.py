from django import template

register = template.Library()


@register.filter
def get_value(dict_value, key):
    return dict_value[key]

