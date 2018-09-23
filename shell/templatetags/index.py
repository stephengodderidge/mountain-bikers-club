from django import template

register = template.Library()


@register.filter
def index(a_list, i):
    return a_list[int(i)]
