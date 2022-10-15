from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.decorators import archived_not_available
from registration.models import Event
from registration.permissions import has_access, ACCESS_CORONA_VIEW

from ..export import excel_export
from .utils import notactive

import logging

logger = logging.getLogger("helfertool.corona")


@login_required
@never_cache
@archived_not_available
def data(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permissions
    if not has_access(request.user, event, ACCESS_CORONA_VIEW):
        return nopermission(request)

    # check if corona contact tracing is active
    if not event.corona:
        return notactive(request)

    num_missing = event.helper_set.filter(contacttracingdata__isnull=True).count()

    # render page
    context = {"event": event, "num_missing": num_missing}
    return render(request, "corona/data.html", context)


@login_required
@never_cache
@archived_not_available
def missing(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permissions
    if not has_access(request.user, event, ACCESS_CORONA_VIEW):
        return nopermission(request)

    # check if corona contact tracing is active
    if not event.corona:
        return notactive(request)

    helpers = event.helper_set.filter(contacttracingdata__isnull=True)

    # render page
    context = {"event": event, "helpers": helpers}
    return render(request, "corona/missing.html", context)


@login_required
@never_cache
@archived_not_available
def export(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permissions
    if not has_access(request.user, event, ACCESS_CORONA_VIEW):
        return nopermission(request)

    # check if corona contact tracing is active
    if not event.corona:
        return notactive(request)

    logger.info(
        "corona export",
        extra={
            "user": request.user,
            "event": event,
        },
    )

    # start http response
    filename = "{} - {}.xlsx".format(event.name, _("Corona contact tracing"))
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename

    # close buffer, send file
    data = excel_export(event)
    response.write(data)

    return response
