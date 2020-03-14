from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from registration.decorators import archived_not_available
from registration.models import Event, Helper
from registration.views.utils import nopermission
from registration.permissions import has_access, ACCESS_PREREQUISITES_VIEW

from .utils import notactive

from ..models import Prerequisite


@login_required
@archived_not_available
def view_helpers_prerequisite(request, event_url_name, prerequisite_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check if feature is active
    if not event.prerequisites:
        return notactive(request)

    # check permission
    if not has_access(request.user, event, ACCESS_PREREQUISITES_VIEW):
        return nopermission(request)

    prerequisite = get_object_or_404(Prerequisite, pk=prerequisite_pk)

    if prerequisite.event != event:
        raise Http404

    # find all helpers that need this prerequisite
    helpers = Helper.objects.filter(shifts__job__prerequisites=prerequisite).distinct()

    # render page
    context = {'event': event,
               'prerequisite': prerequisite,
               'helpers': helpers}
    return render(request, 'prerequisites/view_helpers_prerequisite.html', context)
