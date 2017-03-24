from django.contrib.auth.decorators import login_required
from django.db.models import Sum, ExpressionWrapper, F, fields
from django.shortcuts import render, get_object_or_404

from collections import OrderedDict

from registration.decorators import archived_not_available
from registration.models import Event, Shift

from registration.views.utils import nopermission


@login_required
@archived_not_available
def overview(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not event.is_admin(request.user):
        return nopermission(request)

    num_helpers = event.helper_set.count()

    num_coordinators = 0
    timeline = {}
    for helper in event.helper_set.all():
        if helper.is_coordinator:
            num_coordinators += 1
        else:
            day = helper.timestamp.strftime('%Y-%m-%d')
            if day in timeline:
                timeline[day] += 1
            else:
                timeline[day] = 1

    num_vegetarians = event.helper_set.filter(vegetarian=True).count()

    num_shift_slots = Shift.objects.filter(job__event=event).aggregate(
        Sum('number'))['number__sum']

    total_duration = ExpressionWrapper((F('end') - F('begin')) * F('number'),
                                       output_field=fields.DurationField())
    hours_total = Shift.objects.filter(job__event=event) \
                       .annotate(duration=total_duration) \
                       .aggregate(Sum('duration'))['duration__sum']

    # sum up timeline
    timeline = OrderedDict(sorted(timeline.items()))
    timeline_sum = OrderedDict()
    tmp = 0
    for day in timeline:
        tmp += timeline[day]
        timeline_sum[day] = tmp

    # render
    context = {'event': event,
               'num_helpers': num_helpers,
               'num_coordinators': num_coordinators,
               'num_vegetarians': num_vegetarians,
               'num_shift_slots': num_shift_slots,
               'hours_total': hours_total,
               'timeline': timeline_sum}
    return render(request, 'statistic/overview.html', context)
