from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

from registration.decorators import archived_not_available
from registration.views.utils import nopermission, get_or_404
from registration.permissions import has_access, ACCESS_GIFTS_HANDLE

from .utils import notactive

from ..forms import PresentForm


@login_required
@archived_not_available
def set_present(request, event_url_name, shift_pk):
    event, job, shift, helper = get_or_404(event_url_name, shift_pk=shift_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_GIFTS_HANDLE):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    form = PresentForm(request.POST or None, shift=shift)

    if form.is_valid():
        form.save()

        messages.success(request, _("Attendance was saved"))

        return HttpResponseRedirect(reverse('gifts:set_present',
                                    args=[event.url_name, shift.pk, ]))

    context = {'event': event,
               'shift': shift,
               'form': form}
    return render(request, 'gifts/set_present.html', context)
