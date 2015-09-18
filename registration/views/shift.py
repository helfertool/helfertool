from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

from .utils import nopermission, get_or_404

from ..forms import ShiftForm, ShiftDeleteForm


@login_required
def edit_shift(request, event_url_name, job_pk, shift_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, job_pk, shift_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = ShiftForm(request.POST or None, instance=shift, job=job)

    if form.is_valid():
        job = form.save()
        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # render page
    context = {'event': job.event,
               'job': job,
               'shift': shift,
               'form': form}
    return render(request, 'registration/admin/edit_shift.html', context)


@login_required
def delete_shift(request, event_url_name, job_pk, shift_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk, shift_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = ShiftDeleteForm(request.POST or None, instance=shift)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Shift deleted"))

        # redirect to shift
        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # render page
    context = {'event': event,
               'shift': shift,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/delete_shift.html', context)
