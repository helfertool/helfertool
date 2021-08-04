from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from helfertool.utils import nopermission
from registration.models import Event

from ..models import SentMail


@login_required
def show_mail(request, event_url_name, mail_pk):
    event = get_object_or_404(Event, url_name=event_url_name)
    mail = get_object_or_404(SentMail, pk=mail_pk)

    # check permission
    if not mail.can_see_mail(request.user):
        return nopermission(request)

    # render page
    context = {'event': event,
               'mail': mail}
    return render(request, 'mail/show_mail.html', context)
