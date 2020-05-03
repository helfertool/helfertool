from django import template

register = template.Library()


@register.simple_tag
def helper_has_fulfilled_prerequisite(helper, prerequisite):
    return prerequisite.check_helper(helper)


@register.simple_tag
def lookup_prerequisite(form, name):
    return form[name]