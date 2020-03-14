from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from ..models import Event, Job, Helper, Shift, Duplicate


def nopermission(request):
    return render(request, 'registration/admin/nopermission.html')


def get_or_404(event_url_name=None, job_pk=None, shift_pk=None,
               helper_pk=None, handle_duplicates=False):

    # default values
    event, job, shift, helper = None, None, None, None

    # get all data, if needed
    if event_url_name:
        event = get_object_or_404(Event, url_name=event_url_name)
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)
    if shift_pk:
        shift = get_object_or_404(Shift, pk=shift_pk)

    try:
        if helper_pk:
            # check if the current helper_pk belongs to a deleted duplicate
            if handle_duplicates:
                try:
                    helper_pk = Duplicate.objects.get(deleted=helper_pk) \
                                         .existing.pk
                except Duplicate.DoesNotExist:
                    pass

            # and now get helper
            helper = get_object_or_404(Helper, pk=helper_pk)
    except ValidationError:  # handle misformed uuid
        raise Http404

    # sanity checks
    if event and job and job.event != event:
        raise Http404

    if job and shift and shift.job != job:
        raise Http404

    if shift and helper and not helper.shifts.filter(pk=shift.pk).exists():
        raise Http404

    # return data
    return event, job, shift, helper
