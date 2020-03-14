from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

from .utils import nopermission, get_or_404

from ..decorators import archived_not_available
from ..forms import ShiftForm, ShiftDeleteForm
from ..permissions import has_access, ACCESS_JOB_EDIT

import logging
logger = logging.getLogger("helfertool")


@login_required
@archived_not_available
def edit_shift(request, event_url_name, job_pk, shift_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, job_pk, shift_pk)

    # check permission
    if not has_access(request.user, job, ACCESS_JOB_EDIT):
        return nopermission(request)

    # form
    form = ShiftForm(request.POST or None, instance=shift, job=job)

    if form.is_valid():
        shift = form.save()

        log_msg = "shift created"
        if shift_pk:
            log_msg = "shift changed"
        logger.info(log_msg, extra={
            'user': request.user,
            'event': event,
            'shift': shift,
        })

        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # render page
    context = {'event': job.event,
               'job': job,
               'shift': shift,
               'form': form}
    return render(request, 'registration/admin/edit_shift.html', context)


@login_required
@archived_not_available
def delete_shift(request, event_url_name, job_pk, shift_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk, shift_pk)

    # check permission
    if not has_access(request.user, job, ACCESS_JOB_EDIT):
        return nopermission(request)

    # form
    form = ShiftDeleteForm(request.POST or None, instance=shift)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Shift deleted"))

        logger.info("shift deleted", extra={
            'user': request.user,
            'event': event,
            'shift': shift,
            'shift_pk': shift_pk,
        })

        # redirect to shift
        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # render page
    context = {'event': event,
               'shift': shift,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/delete_shift.html', context)
