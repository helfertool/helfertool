from django.contrib.auth.decorators import login_required

from registration.views.utils import nopermission

from ..models import Inventory


def inventory_admin_required(function):
    @login_required
    def _decorated(request, *args, **kwargs):
        if request.user.is_superuser or \
                Inventory.objects.filter(admins__exact=request.user).exists():
            return function(request, *args, **kwargs)
        return nopermission(request)

    return _decorated
