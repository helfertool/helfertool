from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Inventory
from ..decorators import inventory_admin_required


@inventory_admin_required
def inventory_list(request):
    inventories = Inventory.objects.all()

    context = {'inventories': inventories}
    return render(request, 'inventory/admin/inventory_list.html',
                  context)
