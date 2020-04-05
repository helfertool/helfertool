from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from registration.decorators import archived_not_available
from registration.models import Event, Helper
from registration.permissions import has_access, ACCESS_INVENTORY_HANDLE
from registration.views.utils import nopermission

from badges.forms import BadgeBarcodeForm

from .utils import notactive
from ..exceptions import WrongHelper, InvalidMultipleAssignment, NotAssigned
from ..forms import InventoryBarcodeForm
from ..models import Item, UsedItem


@login_required
@archived_not_available
def take_back_item(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_INVENTORY_HANDLE):
        return nopermission(request)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    last_helper_pk = request.session.pop('inventory_helper_pk', None)
    try:
        last_helper = Helper.objects.get(pk=last_helper_pk)
        last_helper_items = UsedItem.objects.filter(helper=last_helper,
                                                    timestamp_returned=None)
    except Helper.DoesNotExist:
        last_helper = None
        last_helper_items = None

    form = InventoryBarcodeForm(request.POST or None, event=event)

    not_in_use = False
    if form.is_valid():
        if form.item.is_in_use(event):
            return redirect('inventory:take_back_badge', event_url_name,
                            form.item.pk)
        else:
            not_in_use = True

    context = {'event': event,
               'form': form,
               'not_in_use': not_in_use,
               'last_helper': last_helper,
               'last_helper_items': last_helper_items}
    return render(request, 'inventory/take_back_item.html',
                  context)


@login_required
@archived_not_available
def take_back_badge(request, event_url_name, item_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_INVENTORY_HANDLE):
        return nopermission(request)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    wrong_helper = False
    item = None
    try:
        item = Item.objects.get(pk=item_pk)

        form = BadgeBarcodeForm(request.POST or None, event=event)

        if form.is_valid():
            item.remove_from_helper(form.badge.helper)

            request.session['inventory_helper_pk'] = \
                str(form.badge.helper.pk)

            return redirect('inventory:take_back', event_url_name)
    except (KeyError, Item.DoesNotExist):
        form = None
    except WrongHelper:
        wrong_helper = True

    context = {'event': event,
               'form': form,
               'item': item,
               'wrong_helper': wrong_helper}
    return render(request, 'inventory/take_back_badge.html',
                  context)


@login_required
@archived_not_available
def take_back_direct(request, event_url_name, item_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_INVENTORY_HANDLE):
        return nopermission(request)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    item = Item.objects.get(pk=item_pk)

    try:
        helper = item.get_exclusive_user(event)

        item.remove_from_helper(helper)

        request.session['inventory_helper_pk'] = str(helper.pk)

        return redirect('inventory:take_back', event_url_name)
    except InvalidMultipleAssignment:
        error = 'multiple'
    except NotAssigned:
        error = 'noassignment'

    context = {'event': event,
               'error': error}
    return render(request, 'inventory/take_back_error.html',
                  context)
