from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission

from ..decorators import archived_not_available
from ..models import Event
from ..permissions import has_access, has_access_event_or_job, ACCESS_EVENT_EDIT, ACCESS_EVENT_VIEW_COORDINATORS


@login_required
@never_cache
def admin(request):
    context = {}
    return render(request, "registration/admin/index.html", context)


@login_required
@never_cache
def jobs_and_shifts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT):
        return nopermission(request)

    # list all jobs and shifts
    context = {"event": event}
    return render(request, "registration/admin/jobs_and_shifts.html", context)


@login_required
@never_cache
@archived_not_available
def coordinators(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    if not has_access_event_or_job(request.user, event, ACCESS_EVENT_VIEW_COORDINATORS):
        return nopermission(request)

    context = {"event": event}
    return render(request, "registration/admin/coordinators.html", context)
