from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from .utils import nopermission, get_or_404

from ..decorators import archived_not_available
from ..forms import JobForm, JobDeleteForm, JobDuplicateForm, JobDuplicateDayForm, JobSortForm
from ..models import Event, Job


@login_required
@archived_not_available
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
@archived_not_available
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

    # check if there are coordinators
    helpers_registered = job.coordinators.count() != 0

    # check, if there are helpers registered (if no coordinators were found)
    if not helpers_registered:
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


@login_required
@archived_not_available
def duplicate_job(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = JobDuplicateForm(request.POST or None, other_job=job)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # render page
    context = {'event': event,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/duplicate_job.html', context)


@login_required
@archived_not_available
def duplicate_job_day(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = JobDuplicateDayForm(request.POST or None, job=job)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # render page
    context = {'event': event,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/duplicate_job_day.html', context)


@login_required
@archived_not_available
def sort_job(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = JobSortForm(request.POST or None, event=event)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('jobs_and_shifts',
                                            args=[event_url_name]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/sort_job.html', context)
