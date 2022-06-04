from django import template

register = template.Library()


@register.filter
def mask(value):
    if len(value) <= 3:
        return "*" * len(value)
    if len(value) <= 6:
        return "*"*(len(value)-2) + value[-2:]
    else:
        return value[:2] + "*"*(len(value)-4) + value[-2:]
