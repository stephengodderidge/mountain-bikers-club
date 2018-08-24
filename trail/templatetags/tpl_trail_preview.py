from django import template

register = template.Library()


@register.inclusion_tag('trail/tag_trail_preview.html')
def tpl_trail_preview(trail, url, cell=None):
    return {
        'trail': trail,
        'url': url,
        'cell': cell,
    }
