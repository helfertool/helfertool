from django import template

register = template.Library()


@register.assignment_tag
def active_uses(useditems):
    count = 0
    for tmp in useditems:
        if not tmp.timestamp_returned:
            count += 1
    return count
