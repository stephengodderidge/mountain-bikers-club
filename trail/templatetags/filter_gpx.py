import math

from django import template

register = template.Library()


@register.filter
def format_time(time):
    if not time:
        return 'n/a'

    time_s = float(time)
    minutes = math.floor(time_s / 60.)
    hours = math.floor(minutes / 60.)
    return '%s:%s:%s' % (str(int(hours)).zfill(2), str(int(minutes % 60)).zfill(2), str(int(time_s % 60)).zfill(2))
