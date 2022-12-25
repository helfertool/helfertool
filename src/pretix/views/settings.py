from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.models import Event
from registration.permissions import has_access, ACCESS_CORONA_EDIT, ACCESS_PRETIX_EDIT
from pretix.forms.settings import PretixSettingsForm


import logging

logger = logging.getLogger("helfertool.corona")


@login_required
@never_cache
def settings(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_PRETIX_EDIT):
        return nopermission(request)

    # check if pretix sync is active
    if not event.pretix:
        return render(request, "pretix/not_active.html")

    # form
    form = PretixSettingsForm(data=request.POST or None, event=event)
    if form.is_valid():
        form.save()

        logger.info(
            "pretix settings",
            extra={
                "user": request.user,
                "event": event,
            },
        )

        return redirect("pretix:settings", event_url_name=event.url_name)

    context = {"event": event, "form": form}
    return render(request, "pretix/settings.html", context)
