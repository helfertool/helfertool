from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models.functions import TruncDate
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from .utils import nopermission, get_or_404
from ..forms.helper import HelperCommentForm

from ..models import Event, Job, Shift
from ..forms import HelperForm, HelperDeleteForm, \
    HelperDeleteCoordinatorForm, RegisterForm, HelperAddShiftForm, \
    HelperAddCoordinatorForm, HelperSearchForm, HelperResendMailForm
from ..decorators import archived_not_available

from gifts.forms import HelpersGiftsForm
from prerequisites.forms import HelperPrerequisiteForm

import logging
logger = logging.getLogger("helfertool")


@login_required
def helpers(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # helpers of one job
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

        # check permission
        if not job.is_admin(request.user):
            return nopermission(request)

        is_admin = event.is_admin(request.user)

        shifts_by_day = job.shifts_by_day().items()

        # show list of helpers
        context = {'event': event,
                   'job': job,
                   'shifts_by_day': shifts_by_day,
                   'is_admin': is_admin}
        return render(request, 'registration/admin/helpers_for_job.html',
                      context)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    # list of days with shifts
    days = Shift.objects.filter(job__event=event) \
        .annotate(day=TruncDate('begin')).values_list('day', flat=True) \
        .order_by('day').distinct()

    # overview over jobs
    context = {'event': event,
               'days': days}
    return render(request, 'registration/admin/helpers.html', context)


@login_required
def view_helper(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name,
                                           helper_pk=helper_pk)

    # Permissions for features
    if not helper.can_edit(request.user):
        return nopermission(request)

    edit_badge = event.badges and event.is_admin(request.user)
    edit_gifts = event.gifts and event.is_admin(request.user)
    edit_prerequisites = event.prerequisites and event.is_admin(request.user)

    # we have multiple forms. all of them need to be valid in order to save them
    forms_valid = True

    # internal comment
    helper_form = HelperCommentForm(request.POST or None,
                                    instance=helper)
    if not helper_form.is_valid():
        forms_valid = False


    # gift editing
    gifts_form = None
    if edit_gifts:
        helper.gifts.update()

        gifts_form = HelpersGiftsForm(request.POST or None,
                                      instance=helper.gifts,
                                      prefix="gifts")

        if not gifts_form.is_valid():
            forms_valid = False
        
    # prerequisite editing
    prerequisites_form = None
    if edit_prerequisites:
        prerequisites_form = HelperPrerequisiteForm(request.POST or None,
                                                    helper=helper,
                                                    prefix="prerequisites")
        
        if not prerequisites_form.is_valid():
            forms_valid = False

    # the forms are valid and we have at least one form -> save and redirect
    if forms_valid and (gifts_form or prerequisites_form or helper_form):
        if gifts_form and gifts_form.is_valid():
            gifts_form.save()

        if prerequisites_form and prerequisites_form.is_valid():
            prerequisites_form.save(request)

        if helper_form and helper_form.is_valid():
            helper_form.save()

        messages.success(request, _("Changes were saved."))
        return redirect('view_helper', event_url_name=event.url_name, helper_pk=helper.pk)

    # render page
    context = {'event': event,
               'helper': helper,
               'edit_badge': edit_badge,
               'gifts_form': gifts_form,
               'prerequisites_form': prerequisites_form,
               'helper_form': helper_form,
    }
    return render(request, 'registration/admin/view_helper.html', context)


@login_required
def edit_helper(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not helper.can_edit(request.user):
        return nopermission(request)

    # forms
    form = HelperForm(request.POST or None, instance=helper, event=event)

    if form.is_valid():
        form.save()

        logger.info("helper changed", extra={
            'user': request.user,
            'event': event,
            'helper': helper,
        })

        if form.email_has_changed:
            # we do not know here if it was an internal registration or not, so send the public version
            if not helper.send_mail(request, internal=False):
                messages.error(request, _("Sending the mail failed, but the helper was saved."))

        return HttpResponseRedirect(reverse('view_helper', args=[event_url_name, helper.pk]))

    # render page
    context = {'event': event,
               'helper': helper,
               'form': form}
    return render(request, 'registration/admin/edit_helper.html', context)


@login_required
@archived_not_available
def add_helper(request, event_url_name, shift_pk):
    event, job, shift, helper = get_or_404(event_url_name, shift_pk=shift_pk)

    # check permission
    if not shift.job.is_admin(request.user):
        return nopermission(request)

    # get all shifts of this job
    all_shifts = Shift.objects.filter(job=shift.job)

    form = RegisterForm(request.POST or None, event=event, shifts=all_shifts,
                        selected_shifts=[shift, ], internal=True)

    if form.is_valid():
        helper = form.save()

        logger.info("helper created", extra={
            'user': request.user,
            'event': event,
            'helper': helper,
        })

        if not helper.send_mail(request, internal=True):
            messages.error(request, _("Sending the mail failed, but the helper was saved."))

        return HttpResponseRedirect(reverse('helpers', args=[event_url_name, shift.job.pk]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/add_helper.html', context)


@login_required
@archived_not_available
def add_coordinator(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk=job_pk)

    # check permission
    if not job.is_admin(request.user):
        return nopermission(request)

    # form
    form = HelperForm(request.POST or None, job=job, event=event)

    if form.is_valid():
        helper = form.save()

        logger.info("helper created", extra={
            'user': request.user,
            'event': event,
            'job': job,
            'helper': helper,
        })

        if not helper.send_mail(request, internal=True):
            messages.error(request, _("Sending the mail failed, but the coordinator was saved."))

        return HttpResponseRedirect(reverse('helpers', args=[event_url_name, job.pk]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_helper.html', context)


@login_required
@archived_not_available
def add_helper_to_shift(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    form = HelperAddShiftForm(request.POST or None, helper=helper,
                              user=request.user)

    if form.is_valid():
        form.save()

        # TODO: add shifts
        logger.info("helper newshift", extra={
            'user': request.user,
            'event': event,
            'helper': helper,
        })

        return HttpResponseRedirect(reverse('view_helper',
                                            args=[event_url_name, helper.pk]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/add_helper_to_shift.html',
                  context)


@login_required
@archived_not_available
def add_helper_as_coordinator(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    form = HelperAddCoordinatorForm(request.POST or None, helper=helper,
                                    user=request.user)

    if form.is_valid():
        form.save()

        # TODO: add job
        logger.info("helper newjob", extra={
            'user': request.user,
            'event': event,
            'helper': helper,
        })

        return HttpResponseRedirect(reverse('view_helper',
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

        # TODO: only single shift or completely?
        logger.info("helper deleted", extra={
            'user': request.user,
            'event': event,
            'helper': helper,
            'helper_pk': helper_pk,
        })

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

        # TODO: only one job or completely?
        logger.info("helper deleted", extra={
            'user': request.user,
            'event': event,
            'helper': helper,
            'helper_pk': helper_pk,
        })

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
@archived_not_available
def search_helper(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    # form
    form = HelperSearchForm(request.POST or None, event=event,
                            user=request.user)
    result = None
    new_search = True

    if form.is_valid():
        # input was barcode -> redirect
        helper = form.check_barcode()
        if helper:
            return HttpResponseRedirect(reverse(
                'view_helper', args=[event_url_name, helper.pk]))

        # else show results
        result = form.get()
        new_search = False

    # render page
    context = {'event': event,
               'form': form,
               'result': result,
               'new_search': new_search}
    return render(request, 'registration/admin/search_helper.html', context)


@login_required
@archived_not_available
def resend_mail(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    if not helper.can_edit(request.user):
        return nopermission(request)

    form = HelperResendMailForm(request.POST or None)

    if form.is_valid():
        logger.info("helper confirmationmail", extra={
            'user': request.user,
            'event': event,
            'helper': helper,
        })

        if helper.send_mail(request, internal=False):
            messages.success(request, _("Confirmation mail was sent"))

            # clear error message about undelivered mail
            helper.mail_failed = None
            helper.save()
        else:
            messages.error(request, _("Sending the mail failed."))

        return HttpResponseRedirect(reverse('view_helper', args=[event_url_name, helper.pk]))

    context = {'event': event,
               'helper': helper,
               'form': form}
    return render(request, 'registration/admin/resend_mail.html', context)
