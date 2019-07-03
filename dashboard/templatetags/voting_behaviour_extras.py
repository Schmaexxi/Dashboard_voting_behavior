from django import template
import datetime

register = template.Library()


@register.filter
def dict_access(h, key):
    return h.get(key, 0)


@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)


@register.filter
def date_difference(date):
    return (datetime.date.today() - date).days
