from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.decorators import archived_not_available
from registration.models import Event
from registration.permissions import has_access, ACCESS_CORONA_EDIT

from ..forms import CoronaCleanupForm
from .utils import notactive

import logging

logger = logging.getLogger("helfertool.corona")


@login_required
@never_cache
@archived_not_available
def cleanup(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_CORONA_EDIT):
        return nopermission(request)

    # check if corona contact tracing is active
    if not event.corona:
        return notactive(request)

    # form
    form = CoronaCleanupForm(request.POST or None)
    if form.is_valid():
        form.cleanup(event)

        logger.info(
            "corona cleanup",
            extra={
                "user": request.user,
                "event": event,
            },
        )

        messages.success(request, _("Contact tracing data deleted"))

        return redirect("corona:settings", event_url_name=event.url_name)

    context = {"event": event, "form": form}
    return render(request, "corona/cleanup.html", context)
