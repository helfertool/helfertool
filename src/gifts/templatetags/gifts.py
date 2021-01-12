from django import template

from registration.models.helpershift import HelperShift

register = template.Library()


@register.simple_tag
def lookup_helpersgifts_delivered(form, key):
    return form['delivered_' + str(key)]


@register.simple_tag
def lookup_helpersgifts_present(form, key):
    return form['present_' + str(key)]


@register.simple_tag
def gifts_for_shift(form, shift):
    return form.deservedgifts_for_shift(shift)


@register.simple_tag
def helper_has_missed_shift(helper, shift):
    return helper.has_missed_shift(shift)


@register.simple_tag
def helper_shift_requires_deposit(helper, shift):
    helpershift = HelperShift.objects.get(helper=helper, shift=shift)
    return not helpershift.present
