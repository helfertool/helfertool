from django.shortcuts import render, get_object_or_404, redirect


from registration.decorators import archived_not_available, admin_required
from registration.models import Event

from .utils import notactive
from ..forms import InventorySettingsForm


@archived_not_available
@admin_required
def event_settings(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

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
