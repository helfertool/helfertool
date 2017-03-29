from django import template

from ..models import Inventory

register = template.Library()


@register.assignment_tag
def active_uses(useditems):
    count = 0
    for tmp in useditems:
        if not tmp.timestamp_returned:
            count += 1
    return count


@register.simple_tag(takes_context=True)
def is_inventory_admin(context, inventory):
    if not inventory:
        return False

    return inventory.is_admin(context["user"])

@register.filter
def is_inventory_admin_any(user):
    return Inventory.objects.filter(admins__exact=user).exists()
