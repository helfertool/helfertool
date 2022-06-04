from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.decorators import archived_not_available
from registration.models import Event
from registration.permissions import has_access_event_or_job, ACCESS_MAILS_SEND

from ..forms import MailForm, MailFormError

from smtplib import SMTPException

import logging

logger = logging.getLogger("helfertool.mail")


@login_required
@never_cache
@archived_not_available
def send_mail(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access_event_or_job(request.user, event, ACCESS_MAILS_SEND):
        return nopermission(request)

    # form
    form = MailForm(request.POST or None, event=event, user=request.user)

    if form.is_valid():
        try:
            form.send_mail()
            messages.success(request, _("Mail was sent successfully"))

            logger.info(
                "mail sent",
                extra={
                    "user": request.user,
                    "event": event,
                    "subject": form.cleaned_data["subject"],
                },
            )
        except (SMTPException, ConnectionError, MailFormError) as e:
            messages.error(request, _("Sending mails failed"))

            logger.error(
                "mail error",
                extra={
                    "user": request.user,
                    "event": event,
                    "subject": form.cleaned_data["subject"],
                    "error": str(e),
                },
            )
        return redirect("mail:send", event_url_name=event_url_name)

    # render page
    context = {"event": event, "form": form}
    return render(request, "mail/send_mail.html", context)
