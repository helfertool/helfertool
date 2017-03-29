from django.shortcuts import render, get_object_or_404

from registration.decorators import archived_not_available, admin_required
from registration.models import Event

from .utils import notactive
from ..models import UsedItem


@archived_not_available
@admin_required
def event_list(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    used_items = UsedItem.objects.filter(helper__event=event)

    context = {'event': event,
               'used_items': used_items}
    return render(request, 'inventory/list.html',
                  context)
