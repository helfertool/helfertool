from django.shortcuts import render, get_object_or_404

from registration.views.utils import nopermission, is_involved
from registration.models import Event

from ..models import Gift, GiftSet

from .utils import notactive


def list(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    gifts = Gift.objects.filter(event=event)
    gift_sets = GiftSet.objects.filter(event=event)

    context = {'event': event,
               'gifts': gifts,
               'gift_sets': gift_sets}
    return render(request, 'gifts/list.html', context)
