from django import template

register = template.Library()


@register.filter
def lookup_deservedgiftset(h, key):
    return h['gift_' + str(key)]
