from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from registration.views.utils import nopermission

from ..models import Inventory


def any_inventory_admin_required(function):
    @login_required
    def _decorated(request, *args, **kwargs):
        if request.user.is_superuser or \
                Inventory.objects.filter(admins__exact=request.user).exists():
            return function(request, *args, **kwargs)
        return nopermission(request)

    return _decorated


def inventory_admin_required(function):
    """
    Checks if user has access to inventory.

    Instead of the inventory_pk the inventory object is given to the view.
    """
    @login_required
    def _decorated(request, *args, **kwargs):
        inventory_pk = kwargs.pop('inventory_pk', None)
        inventory = None

        if inventory_pk:
            inventory = get_object_or_404(Inventory, pk=inventory_pk)
            if not inventory.is_admin(request.user):
                return nopermission(request)
        elif not request.user.is_superuser:
            # TODO: introduce new permission to add new inventories
            return nopermission(request)

        return function(request, *args, inventory=inventory, **kwargs)

    return _decorated
