from django import template
from django.conf import settings

from ..permissions import has_access as ext_has_access
from ..permissions import has_access_event_or_job as ext_has_access_event_or_job
from ..permissions import ACCESS_INVOLVED, _check_job_role

register = template.Library()


@register.simple_tag(takes_context=True)
def has_access(context, resource, access):
    if resource is None or access is None:
        return False

    return ext_has_access(context["user"], resource, access)


@register.simple_tag(takes_context=True)
def has_access_event_or_job(context, resource, access_event, access_job):
    if resource is None or access_event is None or access_job is None:
        return False

    return ext_has_access_event_or_job(context["user"], resource, access_event, access_job)


@register.simple_tag(takes_context=True)
def is_job_admin(context, job):
    if not job:
        return False

    # FIXME: change after job admin roles are implemented
    return _check_job_role(context["user"], job, None)