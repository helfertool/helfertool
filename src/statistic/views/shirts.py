from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from collections import OrderedDict

from registration.views.utils import nopermission
from registration.decorators import archived_not_available
from registration.models import Event, Helper
from registration.permissions import has_access, has_access_event_or_job, ACCESS_STATISTICS_VIEW, ACCESS_JOB_VIEW_STATISTICS


class JobShirts:
    def __init__(self, shirt_choices):
        self.shifts = OrderedDict()
        self.total = OrderedDict()

        for size, name in shirt_choices:
            self.total.update({name: 0})


@login_required
@archived_not_available
def shirts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)
    shirt_choices = event.get_shirt_choices()

    # permission
    if not has_access_event_or_job(request.user, event, ACCESS_STATISTICS_VIEW, ACCESS_JOB_VIEW_STATISTICS):
        return nopermission(request)

    # check if shirt sizes are collected for this event
    if not event.ask_shirt:
        context = {'event': event}
        return render(request, 'statistic/shirts_not_active.html', context)

    # size names
    size_names = [name for size, name in shirt_choices]

    # event wide
    total_shirts = OrderedDict()
    coordinator_shirts = OrderedDict()
    if has_access(request.user, event, ACCESS_STATISTICS_VIEW):
        # shirt sizes
        total_shirts_query = event.helper_set.values('shirt').annotate(num=Count('shirt'))
        coordinator_shirts_query = event.all_coordinators.values('shirt').annotate(num=Count('shirt'))

        # total numbers (iterate over all sizes in correct order)
        for size, name in shirt_choices:
            num_total = 0
            num_coordinator = 0

            try:
                num_total = total_shirts_query.get(shirt=size)['num']
            except Helper.DoesNotExist:
                pass

            try:
                num_coordinator = coordinator_shirts_query.get(shirt=size)['num']
            except Helper.DoesNotExist:
                pass

            total_shirts.update({name: num_total})
            coordinator_shirts.update({name: num_coordinator})

    # for each job
    job_shirts = OrderedDict()
    for job in event.job_set.all():
        # check permission for job
        if not has_access(request.user, job, ACCESS_JOB_VIEW_STATISTICS):
            continue

        sizes_for_job = JobShirts(shirt_choices)
        # for each shift
        for shift in job.shift_set.all():
            sizes_for_shift = shift.shirt_sizes
            sizes_for_job.shifts.update({shift: sizes_for_shift})

            # update total number
            for size, name in shirt_choices:
                num = sizes_for_job.total[name]
                sizes_for_job.total.update({name: num+sizes_for_shift[name]})
        job_shirts.update({job: sizes_for_job})

    # render
    context = {'event': event,
               'size_names': size_names,
               'total_shirts': total_shirts,
               'coordinator_shirts': coordinator_shirts,
               'job_shirts': job_shirts}
    return render(request, 'statistic/shirts.html', context)
