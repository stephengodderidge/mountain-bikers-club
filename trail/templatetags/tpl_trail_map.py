import uuid

from django import template

register = template.Library()


@register.inclusion_tag('trail/tag_trail_map.html')
def tpl_trail_map(file, css_height=None, interface=True):
    return {
        'file': file,
        'uid': uuid.uuid4(),
        'css_height': css_height,
        'interface': interface,
    }
