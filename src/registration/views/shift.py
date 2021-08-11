from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission

from ..decorators import archived_not_available
from ..forms import ShiftForm, ShiftDeleteForm
from ..permissions import has_access, ACCESS_JOB_EDIT
from ..utils import get_or_404

import logging
logger = logging.getLogger("helfertool.registration")


@login_required
@never_cache
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

        return redirect('jobs_and_shifts', event_url_name=event_url_name)

    # render page
    context = {'event': job.event,
               'job': job,
               'shift': shift,
               'form': form}
    return render(request, 'registration/admin/edit_shift.html', context)


@login_required
@never_cache
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
        })

        # redirect to shift
        return redirect('jobs_and_shifts', event_url_name=event_url_name)

    # render page
    context = {'event': event,
               'shift': shift,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/delete_shift.html', context)
