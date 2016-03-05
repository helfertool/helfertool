from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from .utils import nopermission, get_or_404

from ..models import Event, Job, Shift
from ..forms import HelperForm, HelperDeleteForm, \
    HelperDeleteCoordinatorForm, RegisterForm, HelperAddShiftForm, \
    HelperAddCoordinatorForm, HelperSearchForm

from badges.forms import BadgeForm


@login_required
def helpers(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    # helpers of one job
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

        # check permission
        if not job.is_admin(request.user):
            return nopermission(request)

        # show list of helpers
        context = {'event': event, 'job': job}
        return render(request, 'registration/admin/helpers_for_job.html',
                      context)

    # overview over jobs
    context = {'event': event}
    return render(request, 'registration/admin/helpers.html', context)


@login_required
def edit_helper(request, event_url_name, helper_pk, job_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not helper.can_edit(request.user):
        return nopermission(request)

    # badges active and permission?
    edit_badges = event.badges and event.is_admin(request.user)

    # forms
    form = HelperForm(request.POST or None, instance=helper, event=event)
    badge_form = None
    if edit_badges:
        badge_form = BadgeForm(request.POST or None, request.FILES or None,
                               instance=helper.badge,
                               prefix='badge')

    if form.is_valid() and (not edit_badges or
                            (badge_form and badge_form.is_valid())):
        form.save()

        if edit_badges:
            badge_form.save()

        # check if job_pk is given -> redirect to helpers of this job
        if job_pk:
            return HttpResponseRedirect(reverse('helpers',
                                                args=[event_url_name, job_pk]))
        else:
            # else redirect to helpers overview
            return HttpResponseRedirect(reverse('helpers',
                                                args=[event_url_name]))

    # render page
    context = {'event': event,
               'helper': helper,
               'form': form,
               'badge_form': badge_form}
    return render(request, 'registration/admin/edit_helper.html', context)


@login_required
def add_helper(request, event_url_name, shift_pk):
    event, job, shift, helper = get_or_404(event_url_name, shift_pk=shift_pk)

    # check permission
    if not shift.job.is_admin(request.user):
        return nopermission(request)

    # get all shifts of this job
    all_shifts = Shift.objects.filter(job=shift.job)

    form = RegisterForm(request.POST or None, event=event, shifts=all_shifts,
                        selected_shifts=[shift, ], skip_full_age=True)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('helpers',
                                            args=[event_url_name,
                                                  shift.job.pk]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/add_helper.html', context)


@login_required
def add_coordinator(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk=job_pk)

    # check permission
    if not job.is_admin(request.user):
        return nopermission(request)

    # form
    form = HelperForm(request.POST or None, job=job, event=event)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('helpers',
                                            args=[event_url_name, job.pk]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_helper.html', context)


@login_required
def add_helper_to_shift(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    form = HelperAddShiftForm(request.POST or None, helper=helper,
                              user=request.user)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('edit_helper',
                                            args=[event_url_name, helper.pk]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/add_helper_to_shift.html',
                  context)


@login_required
def add_helper_as_coordinator(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    form = HelperAddCoordinatorForm(request.POST or None, helper=helper,
                                    user=request.user)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('edit_helper',
                                            args=[event_url_name, helper.pk]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/add_helper_as_coordinator.html',
                  context)


@login_required
def delete_helper(request, event_url_name, helper_pk, shift_pk,
                  show_all_shifts=False):
    event, job, shift, helper = get_or_404(event_url_name,
                                           shift_pk=shift_pk,
                                           helper_pk=helper_pk)

    # additional plausibility checks
    if shift not in helper.shifts.all():
        raise Http404

    # check permission
    if not helper.can_edit(request.user):
        return nopermission(request)

    # form
    form = HelperDeleteForm(request.POST or None, instance=helper, shift=shift,
                            user=request.user, show_all_shifts=show_all_shifts)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Helper deleted: %(name)s") %
                         {'name': helper.full_name})

        # redirect to shift
        return HttpResponseRedirect(reverse('helpers', args=[event_url_name,
                                                             shift.job.pk]))

    # render page
    context = {'event': event,
               'helper': helper,
               'shift': shift,
               'form': form,
               'show_all_shifts': show_all_shifts}
    return render(request, 'registration/admin/delete_helper.html', context)


@login_required
def delete_coordinator(request, event_url_name, helper_pk, job_pk):
    event, job, shift, helper = get_or_404(event_url_name,
                                           job_pk=job_pk,
                                           helper_pk=helper_pk)

    # check permission
    if not job.is_admin(request.user):
        return nopermission(request)

    # additional plausibility checks
    if helper not in job.coordinators.all():
        raise Http404

    # form
    form = HelperDeleteCoordinatorForm(request.POST or None, instance=helper,
                                       job=job)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Coordinator %(name)s from job "
                                    "\"%(jobname)s\"") %
                         {'name': helper.full_name, 'jobname': job.name})

        # redirect to shift
        return HttpResponseRedirect(reverse('helpers', args=[event_url_name,
                                                             job.pk]))

    # render page
    context = {'event': event,
               'helper': helper,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/delete_coordinator.html',
                  context)


@login_required
def search_helper(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    # form
    form = HelperSearchForm(request.POST or None, event=event)
    result = None
    new_search = True

    if form.is_valid():
        result = form.get()
        new_search = False

    # render page
    context = {'event': event,
               'form': form,
               'result': result,
               'new_search': new_search}
    return render(request, 'registration/admin/search_helper.html', context)
