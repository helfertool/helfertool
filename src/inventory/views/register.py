from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from registration.decorators import archived_not_available
from registration.models import Event, Helper
from registration.permissions import has_access, ACCESS_INVENTORY_HANDLE
from registration.views.utils import nopermission

from badges.forms import BadgeBarcodeForm

from .utils import notactive
from ..exceptions import AlreadyAssigned
from ..forms import InventoryBarcodeForm
from ..models import Item, UsedItem


@login_required
@archived_not_available
def register_item(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_INVENTORY_HANDLE):
        return nopermission(request)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    # data from last registration
    last_helper_pk = request.session.pop('inventory_helper_pk', None)
    last_item_name = request.session.pop('inventory_item_name', None)
    try:
        last_helper = Helper.objects.get(pk=last_helper_pk)
        last_helper_items = UsedItem.objects.filter(helper=last_helper,
                                                    timestamp_returned=None)
    except Helper.DoesNotExist:
        last_helper = None
        last_helper_items = None

    # form for new registration
    form = InventoryBarcodeForm(request.POST or None, event=event)

    not_available = False
    if form.is_valid():
        if form.item.is_available(event):
            return redirect('inventory:register_badge', event_url_name,
                            form.item.pk)
        else:
            not_available = True

    context = {'event': event,
               'form': form,
               'not_available': not_available,
               'last_helper': last_helper,
               'last_helper_items': last_helper_items,
               'last_item_name': last_item_name}
    return render(request, 'inventory/register_item.html',
                  context)


@login_required
@archived_not_available
def register_badge(request, event_url_name, item_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_INVENTORY_HANDLE):
        return nopermission(request)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    already_assigned = False
    try:
        item = Item.objects.get(pk=item_pk)

        form = BadgeBarcodeForm(request.POST or None, event=event)

        if form.is_valid():
            item.add_to_helper(form.badge.helper)

            # update saved data in session
            request.session['inventory_helper_pk'] = str(form.badge.helper.pk)
            request.session['inventory_item_name'] = item.name

            return redirect('inventory:register', event_url_name)
    except (KeyError, Item.DoesNotExist):
        form = None
    except AlreadyAssigned:
        already_assigned = True

    context = {'event': event,
               'form': form,
               'already_assigned': already_assigned}
    return render(request, 'inventory/register_badge.html',
                  context)
