from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from ..models import Inventory, Item
from ..forms import InventoryForm, InventoryDeleteForm, ItemForm, ItemDeleteForm
from ..decorators import any_inventory_admin_required, inventory_admin_required


@any_inventory_admin_required
def inventory_list(request):
    # check if feature is available
    if not settings.FEATURES_INVENTORY:
        raise Http404

    inventories = Inventory.objects.all()

    context = {'inventories': inventories}
    return render(request, 'inventory/admin/inventory_list.html',
                  context)


@inventory_admin_required
def edit_inventory(request, inventory=None):
    # check if feature is available
    if not settings.FEATURES_INVENTORY:
        raise Http404

    # permission checking is done in inventory_admin_required
    form = InventoryForm(request.POST or None, instance=inventory)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('inventory:inventory_list'))

    # render page
    context = {'form': form}
    return render(request, 'inventory/admin/edit_inventory.html', context)


@inventory_admin_required
def delete_inventory(request, inventory):
    # check if feature is available
    if not settings.FEATURES_INVENTORY:
        raise Http404

    # permission checking is done in inventory_admin_required
    form = InventoryDeleteForm(request.POST or None, instance=inventory)

    if form.is_valid():
        form.delete()
        return HttpResponseRedirect(reverse('inventory:inventory_list'))

    # render page
    context = {'inventory': inventory,
               'form': form}
    return render(request, 'inventory/admin/delete_inventory.html', context)


@inventory_admin_required
def inventory_items(request, inventory):
    # check if feature is available
    if not settings.FEATURES_INVENTORY:
        raise Http404

    # permission checking is done in inventory_admin_required
    context = {'inventory': inventory,
               'items': inventory.item_set.all()}
    return render(request, 'inventory/admin/inventory_items.html', context)


@inventory_admin_required
def edit_item(request, inventory, item_pk=None):
    # check if feature is available
    if not settings.FEATURES_INVENTORY:
        raise Http404

    item = None
    if item_pk:
        item = get_object_or_404(Item, pk=item_pk)

        if item.inventory != inventory:
            raise Http404()

    form = ItemForm(request.POST or None, instance=item, inventory=inventory)

    if form.is_valid():
        # TODO: handle unique_together constraint
        form.save()
        return HttpResponseRedirect(reverse('inventory:inventory_items',
                                    args=[inventory.pk]))

    context = {'form': form}
    return render(request, 'inventory/admin/edit_item.html', context)


@inventory_admin_required
def delete_item(request, inventory, item_pk):
    # check if feature is available
    if not settings.FEATURES_INVENTORY:
        raise Http404

    item = get_object_or_404(Item, pk=item_pk)

    if item.inventory != inventory:
        raise Http404()

    form = ItemDeleteForm(request.POST or None, instance=item)

    if form.is_valid():
        form.delete()
        return HttpResponseRedirect(reverse('inventory:inventory_items',
                                    args=[inventory.pk]))

    # render page
    context = {'item': item,
               'form': form}
    return render(request, 'inventory/admin/delete_item.html', context)
