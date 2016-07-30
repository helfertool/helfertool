from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from smtplib import SMTPException

from registration.decorators import archived_not_available
from registration.models import Event
from registration.views.utils import nopermission

from ..forms import MailForm


@login_required
@archived_not_available
def send_mail(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    # form
    form = MailForm(request.POST or None, event=event, user=request.user)

    if form.is_valid():
        try:
            form.send_mail()
            messages.success(request, _("Mail was sent successfully"))
        except (SMTPException, ConnectionError) as e:
            messages.error(request, _("Sending mails failed: %(error)s") %
                           {'error': str(e)})

        return HttpResponseRedirect(reverse('mail', args=[event_url_name]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'mail/send_mail.html', context)
