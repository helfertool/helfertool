from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from collections import OrderedDict
from django.db.models.functions import TruncDate

from .utils import nopermission

from ..models import Event, Shift
from ..decorators import archived_not_available
from ..permissions import has_access, ACCESS_INVOLVED


@login_required
@archived_not_available
def vacant_shifts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_INVOLVED):
        return nopermission(request)

    # first, get all days
    days = Shift.objects.filter(job__event=event) \
        .annotate(day=TruncDate('begin')).values_list('day', flat=True) \
        .order_by('day').distinct()

    # then check every day for vacant shifts
    jobs = event.job_set.all()
    vacant_days = OrderedDict()
    for day in days:
        vacant_jobs_on_day = OrderedDict()
        for job in jobs:
            vacant_shifts_on_day = []
            shifts = job.shift_set.filter(begin__date=day)

            for shift in shifts:
                if not shift.is_full():
                    shift.num_vacant = shift.number - shift.num_helpers()
                    vacant_shifts_on_day.append(shift)

            if vacant_shifts_on_day:
                vacant_jobs_on_day[job] = vacant_shifts_on_day

        if vacant_jobs_on_day:
            vacant_days[day] = vacant_jobs_on_day

    context = {'event': event,
               'no_shifts': len(days) == 0,
               'vacant_days': vacant_days}
    return render(request, 'registration/admin/vacant_shifts.html', context)
