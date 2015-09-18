from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from .utils import nopermission, get_or_404

from ..models import Event, Job
from ..forms import JobForm, JobDeleteForm


@login_required
def edit_job(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # get job, if available
    job = None
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

    # form
    form = JobForm(request.POST or None, instance=job, event=event)

    if form.is_valid():
        job = form.save()
        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # render page
    context = {'event': event,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/edit_job.html', context)


@login_required
def delete_job(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = JobDeleteForm(request.POST or None, instance=job)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Job deleted: %(name)s") %
                         {'name': job.name})

        # redirect to shift
        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # check, if there are helpers registered
    helpers_registered = False
    for shift in job.shift_set.all():
        if shift.helper_set.count() > 0:
            helpers_registered = True
            break

    # render page
    context = {'event': event,
               'job': job,
               'helpers_registered': helpers_registered,
               'form': form}
    return render(request, 'registration/admin/delete_job.html', context)
