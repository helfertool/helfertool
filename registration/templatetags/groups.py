from django import template
from django.conf import settings
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def has_group(user, groupname):
    return user.groups.filter(name=groupname).exists()

@register.filter
def has_adduser_group(user):
    return has_group(user, settings.GROUP_ADDUSER)

@register.filter
def has_addevent_group(user):
    return has_group(user, settings.GROUP_ADDEVENT)

@register.filter
def has_perm_group(user):
    return has_group(user, settings.GROUP_ADDUSER) or \
           has_group(user, settings.GROUP_ADDEVENT)
