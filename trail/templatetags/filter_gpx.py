import math

from django import template
from ..utils.gpx import get_track_details

register = template.Library()


@register.filter
def format_time(time):
    if not time:
        return 'n/a'

    time_s = float(time)
    minutes = math.floor(time_s / 60.)
    hours = math.floor(minutes / 60.)
    return '%s:%s:%s' % (str(int(hours)).zfill(2), str(int(minutes % 60)).zfill(2), str(int(time_s % 60)).zfill(2))


@register.filter
def details(track):
    return get_track_details(track)
