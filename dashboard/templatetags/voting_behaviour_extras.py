from django import template

register = template.Library()


@register.filter
def dict_access(h, key):
    return h[f"{key}"]
