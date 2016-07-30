from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from registration.models import Event
from registration.views.utils import nopermission


@login_required
def list_mails(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    # render page
    context = {'event': event}
    return render(request, 'mail/list_mails.html', context)
