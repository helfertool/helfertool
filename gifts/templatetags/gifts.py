from django import template

register = template.Library()


@register.filter
def lookup_deservedgiftset(h, key):
    return h['gift_' + str(key)]

@register.assignment_tag
def gifts_for_shift(form, shift):
    return form.deservedgifts_for_shift(shift)
