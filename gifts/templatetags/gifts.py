from django import template

register = template.Library()


@register.filter
def lookup_deservedgiftset_delivered(h, key):
    return h['delivered_' + str(key)]

@register.filter
def lookup_deservedgiftset_present(h, key):
    return h['present_' + str(key)]

@register.assignment_tag
def gifts_for_shift(form, shift):
    return form.deservedgifts_for_shift(shift)
