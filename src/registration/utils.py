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
    if event and job and job.event != event:
        raise Http404

    if job and shift and shift.job != job:
        raise Http404

    if shift and helper and not helper.shifts.filter(pk=shift.pk).exists():
        raise Http404

    # and return data
    return event, job, shift, helper
