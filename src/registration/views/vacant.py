from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from collections import OrderedDict
from django.db.models.functions import TruncDate, TruncTime
from pprint import pprint

from .utils import nopermission

from ..models import Event, Shift
from ..decorators import archived_not_available

import logging
logger = logging.getLogger("helfertool")

@login_required
def vacant_shifts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    days = Shift.objects.filter(job__event=event) \
        .annotate(day=TruncDate('begin')).values_list('day', flat=True) \
        .order_by('day').distinct()
        
    jobs = event.job_set.all()
    daysDict = OrderedDict()
    for day in days:
        jobDict = OrderedDict()
        for job in jobs:
            shiftList = []
            shifts = job.shift_set.filter(begin__date=day) \
                .annotate(time_begin=TruncTime('begin')) \
                .annotate(time_end=TruncTime('end'))
            for shift in shifts:
                if not shift.is_full():
                    shift.num_vacant = shift.number - shift.num_helpers()
                    shift.percent_vacant = 100 - shift.helpers_percent()
                    shiftList.append(shift)
            if shiftList:
                jobDict[job] = shiftList
        if jobDict:
            daysDict[day] = jobDict 

    context = {'event': event,
                'days': daysDict}
    return render(request, 'registration/admin/jobs_and_shifts_vacant.html', context)