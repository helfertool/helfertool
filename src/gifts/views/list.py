from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render, get_object_or_404

from collections import OrderedDict

from registration.decorators import archived_not_available
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
@archived_not_available
def list_deposit(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    helpers = event.helper_set.filter(gifts__deposit__isnull=False,
                                      gifts__deposit_returned=False)

    if helpers:
        deposit_sum = helpers.aggregate(total=Sum('gifts__deposit'))['total']
    else:
        deposit_sum = None

    context = {'event': event,
               'helpers': helpers,
               'deposit_sum': deposit_sum}
    return render(request, 'gifts/list_deposit.html', context)


@login_required
@archived_not_available
def list_shirts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    if event.ask_shirt:
        helpers = event.helper_set.filter(gifts__buy_shirt=True)

        num_shirts = OrderedDict()
        shirts = helpers.values('shirt').annotate(num=Count('shirt'))
        for size, name in event.get_shirt_choices():
            num = 0

            try:
                num = shirts.get(shirt=size)['num']
            except Helper.DoesNotExist:
                pass

            num_shirts.update({name: num})
    else:
        helpers = None
        num_shirts = None

    context = {'event': event,
               'helpers': helpers,
               'num_shirts': num_shirts,
               'shirts_not_active': not event.ask_shirt}
    return render(request, 'gifts/list_shirts.html', context)
