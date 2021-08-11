from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.decorators import archived_not_available
from registration.models import Event
from registration.permissions import has_access, ACCESS_INVENTORY_EDIT

from ..forms import InventorySettingsForm
from .utils import notactive


@login_required
@never_cache
@archived_not_available
def event_settings(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_INVENTORY_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.inventory:
        return notactive(request)

    form = InventorySettingsForm(request.POST or None, instance=event.inventory_settings)
    if form.is_valid():
        form.save()
        return redirect('inventory:event_settings', event_url_name)

    context = {'event': event,
               'form': form}
    return render(request, 'inventory/event_settings.html',
                  context)
