from django import template

register = template.Library()

@register.filter
def lookup_shift(h, key):
    return h['shift_' + str(key)]
