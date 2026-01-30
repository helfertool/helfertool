from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404

from registration.models import Event, Job, Helper, Shift, Duplicate

import string


def escape_filename(filename):
    """Escape a filename so it includes only valid characters."""
    valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return "".join(char for char in filename if char in valid)


def get_or_404(event_url_name=None, job_pk=None, shift_pk=None, helper_pk=None, handle_duplicates=False):
    """
    Get event, job, shift and helper object (as far as keys are given).
    Validates, if the things belong together (job belongs to event, shift to job, ...).

    If `handle_duplicates` is True, the correct existing helper is returned, even if the ID of a
    merged (and therefore deleted) helper is given. This is useful for URLs that were given to the helper.
    """

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
                    helper_pk = Duplicate.objects.get(deleted=helper_pk).existing.pk
                except Duplicate.DoesNotExist:
                    pass

            # and now get helper
            helper = get_object_or_404(Helper, pk=helper_pk)
    except ValidationError:  # handle misformed uuid
        raise Http404

    # sanity checks
    # event needs to be the same for job, shift and helper
    event_values = [
        event,
        job.event if job is not None else None,
        shift.job.event if shift is not None else None,
        helper.event if helper is not None else None,
    ]
    event_values_not_none = list(filter(lambda e: e is not None, event_values))
    if event_values_not_none:
        # all(...) checks if all events are the same
        if not all(e == event_values_not_none[0] for e in event_values_not_none):
            raise Http404

    # helper needs to belong to shift
    if helper and shift and not helper.shifts.filter(pk=shift.pk).exists():
        raise Http404

    # helper needs to belong to job
    if helper and job and job not in helper.all_jobs:
        raise Http404

    # shift needs to belong to job
    if job and shift and shift.job != job:
        raise Http404

    # and return data
    return event, job, shift, helper
