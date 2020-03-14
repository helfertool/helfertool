from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from registration.decorators import archived_not_available
from registration.models import Event
from registration.permissions import has_access, ACCESS_INVENTORY_HANDLE
from registration.views.utils import nopermission

from .utils import notactive
from ..models import UsedItem


@login_required
@archived_not_available
def event_list(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_INVENTORY_HANDLE):
        return nopermission(request)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    used_items = UsedItem.objects.filter(helper__event=event)

    context = {'event': event,
               'used_items': used_items}
    return render(request, 'inventory/list.html',
                  context)
