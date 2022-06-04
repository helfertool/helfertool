from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.models import Event
from registration.permissions import has_access, ACCESS_CORONA_EDIT

from ..forms import CoronaSettingsForm
from .utils import notactive

import logging

logger = logging.getLogger("helfertool.corona")


@login_required
@never_cache
def settings(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_CORONA_EDIT):
        return nopermission(request)

    # check if corona contact tracing is active
    if not event.corona:
        return notactive(request)

    # form
    form = CoronaSettingsForm(request.POST or None, instance=event.corona_settings)
    if form.is_valid():
        form.save()

        logger.info(
            "corona settings",
            extra={
                "user": request.user,
                "event": event,
            },
        )

        return redirect("corona:settings", event_url_name=event.url_name)

    context = {"event": event, "form": form}
    return render(request, "corona/settings.html", context)
