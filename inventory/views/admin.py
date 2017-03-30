from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..models import Inventory
from ..forms import InventoryForm
from ..decorators import any_inventory_admin_required, inventory_admin_required


@any_inventory_admin_required
def inventory_list(request):
    inventories = Inventory.objects.all()

    context = {'inventories': inventories}
    return render(request, 'inventory/admin/inventory_list.html',
                  context)

@inventory_admin_required
def edit_inventory(request, inventory=None):
    # permission checking is done in inventory_admin_required

    form = InventoryForm(request.POST or None, instance=inventory)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('inventory:inventory_list'))

    # render page
    context = {'form': form}
    return render(request, 'inventory/admin/edit_inventory.html', context)
