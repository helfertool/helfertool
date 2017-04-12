from django.template import Library
from django.template.defaultfilters import stringfilter
from latex import escape

register = Library()

@register.filter
@stringfilter
def latex(value):
    try:
        return escape(value)
    except:
        return ''


@register.filter
def bykey(value, arg):
    try:
        return value[arg]
    except:
        return ''

