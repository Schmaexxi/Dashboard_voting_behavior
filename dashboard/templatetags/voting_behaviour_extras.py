from typing import Any, Dict, Union, Iterable
from django import template
import datetime

register = template.Library()


@register.filter
def dict_access(h: Dict[str, Dict[str, int]], key: str) -> Any:
    """
    dictionary acess
    :param h: some dictionary
    :param key: key to access
    :return: object or 0
    """
    return h.get(key, 0)


@register.filter(name='zip')
def zip_lists(a: Iterable[Any], b: Iterable[Any]) -> zip:
    """
    zip two iterables
    :param a: some list
    :param b: some list
    :return: zip object
    """
    return zip(a, b)


@register.filter
def date_difference(date: datetime.date) -> datetime.timedelta.days:
    """
    calculates the difference in days between today and a given date
    :param date: varaible of type datetime.date
    :return:  number of days
    """
    return (datetime.date.today() - date).days
