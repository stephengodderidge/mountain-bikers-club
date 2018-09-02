from django import template

register = template.Library()


@register.inclusion_tag('discover/tag_button.html')
def tpl_button(label, link=None, *args, **kwargs):
    class_name = kwargs['class'] if 'class' in kwargs else None
    return {
        'label': label,
        'link': link,
        'class': class_name,
    }
