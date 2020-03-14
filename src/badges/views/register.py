from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from ..forms import BadgeBarcodeForm

from registration.decorators import archived_not_available
from registration.views.utils import nopermission
from registration.models import Event
from registration.permissions import has_access, ACCESS_BADGES_GENERATE

from .utils import notactive


@login_required
@archived_not_available
def register(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_GENERATE):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    if event.badge_settings.barcodes:
        form = BadgeBarcodeForm(request.POST or None, event=event)

        if form.is_valid():
            if form.badge.printed:
                # duplicate -> error
                messages.error(request, _("Badge already printed: %(name)s") %
                               {'name': form.badge.helper.full_name})
            else:
                # mark as printed
                form.badge.printed = True
                form.badge.save()
                messages.success(request, _("Badge registered: %(name)s") %
                                 {'name': form.badge.helper.full_name})
    else:
        form = None

    context = {'event': event,
               'form': form}
    return render(request, 'badges/register.html',
                  context)
