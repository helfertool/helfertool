from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission

from ..decorators import archived_not_available
from ..forms import (
    JobForm,
    JobAdminRolesForm,
    JobAdminRolesAddForm,
    JobDeleteForm,
    JobDuplicateForm,
    JobDuplicateDayForm,
    JobSortForm,
)
from ..models import Event, Job, JobAdminRoles
from ..permissions import has_access, ACCESS_EVENT_EDIT_JOBS, ACCESS_JOB_EDIT
from ..utils import get_or_404

import logging

logger = logging.getLogger("helfertool.registration")


@login_required
@never_cache
@archived_not_available
def edit_job(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # get job, if available and check permission
    job = None
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

        # job exists -> ACCESS_JOB_EDIT
        if not has_access(request.user, job, ACCESS_JOB_EDIT):
            return nopermission(request)
    else:
        # newly created -> ACCESS_EVENT_EDIT_JOBS
        if not has_access(request.user, event, ACCESS_EVENT_EDIT_JOBS):
            return nopermission(request)

    # form
    form = JobForm(request.POST or None, instance=job, event=event)

    if form.is_valid():
        job = form.save()

        log_msg = "job created"
        if job_pk:
            log_msg = "job changed"
        logger.info(
            log_msg,
            extra={
                "user": request.user,
                "event": event,
                "job": job,
            },
        )

        return redirect(f"{reverse('jobs_and_shifts', kwargs={'event_url_name': event_url_name})}#job_{job.pk}")

    # render page
    context = {"event": event, "job": job, "form": form}
    return render(request, "registration/admin/edit_job.html", context)


@login_required
@never_cache
def edit_job_admins(request, event_url_name, job_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not has_access(request.user, job, ACCESS_JOB_EDIT):
        return nopermission(request)

    # one form per existing admin (differentiated by prefix)
    all_forms = []
    job_admin_roles = JobAdminRoles.objects.filter(job=job)
    for job_admin in job_admin_roles:
        form = JobAdminRolesForm(
            request.POST or None,
            instance=job_admin,
            prefix="user_{}".format(job_admin.user.pk),
        )
        all_forms.append(form)

    # another form to add one new admin
    add_form = JobAdminRolesAddForm(request.POST or None, prefix="add", job=job)

    # we got a post request -> save
    if request.POST and (all_forms or add_form.is_valid()):
        # remove users without any role from admins (no roles = invalid forms)
        for form in all_forms:
            if form.is_valid():
                if form.has_changed():
                    logger.info(
                        "job adminchanged",
                        extra={
                            "user": request.user,
                            "event": event,
                            "job": job,
                            "changed_user": form.instance.user.username,
                            "roles": ",".join(form.instance.roles),
                        },
                    )
                    form.save()
            else:
                logger.info(
                    "job adminremoved",
                    extra={
                        "user": request.user,
                        "event": event,
                        "job": job,
                        "changed_user": form.instance.user.username,
                    },
                )
                form.instance.delete()

        # and save the form for a new admin
        if add_form.is_valid():
            new_admin = add_form.save()

            if new_admin:
                logger.info(
                    "job adminadded",
                    extra={
                        "user": request.user,
                        "event": event,
                        "job": job,
                        "changed_user": new_admin.user.username,
                        "roles": ",".join(new_admin.roles),
                    },
                )
            return redirect("edit_job_admins", event_url_name=event_url_name, job_pk=job.pk)

    context = {"event": event, "job": job, "forms": all_forms, "add_form": add_form}
    return render(request, "registration/admin/edit_job_admins.html", context)


@login_required
@never_cache
@archived_not_available
def delete_job(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT_JOBS):
        return nopermission(request)

    # form
    form = JobDeleteForm(request.POST or None, instance=job)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Job deleted: %(name)s") % {"name": job.name})

        logger.info(
            "job deleted",
            extra={
                "user": request.user,
                "event": event,
                "job": job,
            },
        )

        # redirect to shift
        return redirect("jobs_and_shifts", event_url_name=event_url_name)

    # check if there are coordinators
    helpers_registered = job.coordinators.count() != 0

    # check, if there are helpers registered (if no coordinators were found)
    if not helpers_registered:
        for shift in job.shift_set.all():
            if shift.helper_set.count() > 0:
                helpers_registered = True
                break

    # render page
    context = {
        "event": event,
        "job": job,
        "helpers_registered": helpers_registered,
        "form": form,
    }
    return render(request, "registration/admin/delete_job.html", context)


@login_required
@never_cache
@archived_not_available
def duplicate_job(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT_JOBS):
        return nopermission(request)

    # form
    form = JobDuplicateForm(request.POST or None, other_job=job)

    if form.is_valid():
        new_job = form.save()

        logger.info(
            "job created",
            extra={
                "user": request.user,
                "event": event,
                "job": new_job,
                "duplicated_from": job.name,
                "duplicated_from_pk": job.pk,
            },
        )

        return redirect(f"{reverse('jobs_and_shifts', kwargs={'event_url_name': event_url_name})}#job_{new_job.pk}")

    # render page
    context = {"event": event, "duplicate_job": job, "form": form}
    return render(request, "registration/admin/edit_job.html", context)


@login_required
@never_cache
@archived_not_available
def duplicate_job_day(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not has_access(request.user, job, ACCESS_JOB_EDIT):
        return nopermission(request)

    # form
    form = JobDuplicateDayForm(request.POST or None, job=job)

    if form.is_valid():
        new_shifts = form.save()

        for shift in new_shifts:
            logger.info(
                "shift created",
                extra={
                    "user": request.user,
                    "event": event,
                    "shift": shift,
                },
            )

        return redirect(f"{reverse('jobs_and_shifts', kwargs={'event_url_name': event_url_name})}#job_{job.pk}")

    # render page
    context = {"event": event, "job": job, "form": form}
    return render(request, "registration/admin/duplicate_job_day.html", context)


@login_required
@never_cache
@archived_not_available
def sort_job(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT_JOBS):
        return nopermission(request)

    # form
    form = JobSortForm(request.POST or None, event=event)

    if form.is_valid():
        form.save()

        logger.info(
            "job sorted",
            extra={
                "user": request.user,
                "event": event,
            },
        )

        return redirect("jobs_and_shifts", event_url_name=event_url_name)

    # render page
    context = {"event": event, "form": form}
    return render(request, "registration/admin/sort_job.html", context)
