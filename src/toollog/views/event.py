from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from registration.decorators import archived_not_available
from registration.models import Event
from registration.permissions import has_access, ACCESS_EVENT_VIEW_AUDITLOGS
from registration.views.utils import nopermission

from ..models import LogEntry


@login_required
@archived_not_available
def event_audit_log(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_VIEW_AUDITLOGS):
        return nopermission(request)

    # get logs for this event
    all_logs = LogEntry.objects.filter(event=event)

    # paginate
    paginator = Paginator(all_logs, 50)
    page = request.GET.get('page')
    log = paginator.get_page(page)

    # render page
    context = {'event': event,
               'log': log}
    return render(request, 'toollog/event_audit_log.html', context)
