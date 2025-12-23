from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from datetime import datetime
from dateutil.relativedelta import relativedelta

from ..models import EventArchiveAutomation
from ..forms import (
    EventArchiveStatusForm,
    EventArchiveExceptionForm,
)
from ..utils import event_archive_automation_enabled

from helfertool.utils import nopermission
from registration.models import Event
from registration.decorators import archived_not_available

import logging

logger = logging.getLogger("helfertool.registration")


@login_required
@never_cache
def event_archive_status(request):
    if not request.user.is_superuser:
        return nopermission(request)

    # form for months
    months = 3
    if settings.AUTOMATION_EVENTS_ARCHIVE_DEADLINE is not None:
        months = max(settings.AUTOMATION_EVENTS_ARCHIVE_DEADLINE - 1, 0)

    form = EventArchiveStatusForm(request.GET or None, initial={"months": months})
    if form.is_valid():
        months = form.cleaned_data.get("months")

    # get events
    deadline = datetime.today() - relativedelta(months=months)
    events = Event.objects.filter(archived=False, date__lte=deadline).order_by("date")

    context = {
        "form": form,
        "events": events,
        "archive_automation_enabled": event_archive_automation_enabled(),
    }
    return render(request, "adminautomation/event_archive_status.html", context)


@login_required
@never_cache
@archived_not_available
def edit_event_archive_exception(request, event_url_name):
    if not request.user.is_superuser:
        return nopermission(request)

    event = get_object_or_404(Event, url_name=event_url_name)

    form = None
    if event_archive_automation_enabled():
        automation_data, created = EventArchiveAutomation.objects.get_or_create(event=event)
        form = EventArchiveExceptionForm(request.POST or None, instance=automation_data)

        if form.is_valid():
            form.save()

            logger.info(
                "archiveexception changed",
                extra={
                    "user": request.user,
                    "event": event,
                },
            )

            return redirect("adminautomation:event_archive_status")

    # render page
    context = {
        "event": event,
        "form": form,
    }
    return render(request, "adminautomation/edit_event_archive_exception.html", context)
