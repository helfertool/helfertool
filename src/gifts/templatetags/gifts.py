from django import template

from registration.models.helpershift import HelperShift

register = template.Library()


@register.filter
def lookup_deservedgiftset_delivered(h, key):
    return h['delivered_' + str(key)]


@register.filter
def lookup_deservedgiftset_present(h, key):
    return h['present_' + str(key)]


@register.simple_tag
def gifts_for_shift(form, shift):
    return form.deservedgifts_for_shift(shift)


@register.simple_tag
def helper_present_at_shift(helper, shift):
    try:
        helpershift = HelperShift.objects.get(helper=helper, shift=shift)
        if helpershift.present:
            return 'present'
        elif helpershift.manual_presence:
            return 'absent'
    except HelperShift.DoesNotExist:
        pass

    return 'auto'
