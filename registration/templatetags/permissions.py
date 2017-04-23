from django import template
from django.conf import settings

register = template.Library()

# groups


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
def has_sendnews_group(user):
    return has_group(user, settings.GROUP_SENDNEWS)


@register.filter
def has_perm_group(user):
    return has_group(user, settings.GROUP_ADDUSER) or \
           has_group(user, settings.GROUP_ADDEVENT) or \
           has_group(user, settings.GROUP_SENDNEWS)

# admins, involved, job_admins


@register.simple_tag(takes_context=True)
def is_admin(context, event):
    if not event:
        return False

    return event.is_admin(context["user"])


@register.simple_tag(takes_context=True)
def is_involved(context, event):
    if not event:
        return False

    return event.is_involved(context["user"])


@register.simple_tag(takes_context=True)
def is_job_admin(context, job):
    if not job:
        return False

    return job.is_admin(context["user"])
