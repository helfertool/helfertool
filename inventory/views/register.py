from django.shortcuts import render, get_object_or_404, redirect


from registration.decorators import archived_not_available, admin_required
from registration.models import Event

from badges.forms import BadgeBarcodeForm

from .utils import notactive
from ..exceptions import AlreadyAssigned
from ..forms import InventoryBarcodeForm
from ..models import Item


@archived_not_available
@admin_required
def register_item(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    last_helper_name = request.session.pop('inventory_helper_name', None)
    last_item_name = request.session.pop('inventory_item_name', None)

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
               'last_helper_name': last_helper_name,
               'last_item_name': last_item_name}
    return render(request, 'inventory/register_item.html',
                  context)


@archived_not_available
@admin_required
def register_badge(request, event_url_name, item_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    other_assigned_helper = None
    try:
        item = Item.objects.get(pk=item_pk)

        form = BadgeBarcodeForm(request.POST or None, event=event)

        if form.is_valid():
            item.add_to_helper(form.badge.helper)

            # update saved data in session
            request.session['inventory_helper_name'] = \
                form.badge.helper.full_name
            request.session['inventory_item_name'] = item.name

            return redirect('inventory:register', event_url_name)
    except (KeyError, Item.DoesNotExist):
        form = None
    except AlreadyAssigned as e:
        other_assigned_helper = e.helper

    context = {'event': event,
               'form': form,
               'other_assigned_helper': other_assigned_helper}
    return render(request, 'inventory/register_badge.html',
                  context)
