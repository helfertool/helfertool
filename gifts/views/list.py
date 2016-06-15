from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from registration.views.utils import nopermission
from registration.models import Event, Helper

from ..models import Gift, GiftSet

from .utils import notactive


@login_required
def list(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
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

@login_required
def list_deposit(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    helpers = Helper.objects.filter(gifts__deposit__isnull=False,
                                    gifts__deposit_returned=False)

    context = {'event': event,
               'helpers': helpers}
    return render(request, 'gifts/list_deposit.html', context)
