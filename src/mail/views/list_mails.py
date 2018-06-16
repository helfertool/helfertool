from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from registration.models import Event
from registration.views.utils import nopermission

from ..models import SentMail


@login_required
def list_mails(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    all_sent_mails = SentMail.objects.filter(event=event)
    sent_mails = list(filter(lambda s: s.can_see_mail(request.user),
                             all_sent_mails))

    # render page
    context = {'event': event,
               'sent_mails': sent_mails}
    return render(request, 'mail/list_mails.html', context)
