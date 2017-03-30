from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Inventory
from ..decorators import any_inventory_admin_required


@any_inventory_admin_required
def inventory_list(request):
    inventories = Inventory.objects.all()

    context = {'inventories': inventories}
    return render(request, 'inventory/admin/inventory_list.html',
                  context)
