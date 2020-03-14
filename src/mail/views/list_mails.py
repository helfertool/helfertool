from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from registration.models import Event
from registration.views.utils import nopermission
from registration.permissions import has_access_event_or_job, ACCESS_MAILS_VIEW, ACCESS_JOB_VIEW_MAILS

from ..models import SentMail


@login_required
def list_mails(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission, more fine-granular permission checks are made lateron
    if not has_access_event_or_job(request.user, event, ACCESS_MAILS_VIEW, ACCESS_JOB_VIEW_MAILS):
        return nopermission(request)

    all_sent_mails = SentMail.objects.filter(event=event)
    sent_mails = list(filter(lambda s: s.can_see_mail(request.user),
                             all_sent_mails))

    # render page
    context = {'event': event,
               'sent_mails': sent_mails}
    return render(request, 'mail/list_mails.html', context)
