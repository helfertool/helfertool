from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.decorators import archived_not_available
from registration.permissions import has_access, ACCESS_GIFTS_HANDLE_PRESENCE
from registration.utils import get_or_404

from ..forms import PresentForm
from .utils import notactive


@login_required
@never_cache
@archived_not_available
def set_present(request, event_url_name, shift_pk):
    event, job, shift, _helper = get_or_404(event_url_name, shift_pk=shift_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_GIFTS_HANDLE_PRESENCE):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    form = PresentForm(request.POST or None, shift=shift, user=request.user)

    if form.is_valid():
        form.save()

        messages.success(request, _("Presence was saved"))

        return redirect(
            f"{reverse('helpers_for_job', kwargs={'event_url_name': event.url_name, 'job_pk': shift.job.pk})}#{shift.pk}"
        )

    context = {"event": event, "shift": shift, "form": form}
    return render(request, "gifts/set_present.html", context)
