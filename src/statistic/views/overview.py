from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, ExpressionWrapper, F, fields
from django.db.utils import OperationalError
from django.shortcuts import render, get_object_or_404

from registration.decorators import archived_not_available
from registration.models import Event, Shift

from registration.views.utils import nopermission
from registration.permissions import has_access, ACCESS_STATISTICS_VIEW


@login_required
@archived_not_available
def overview(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not has_access(request.user, event, ACCESS_STATISTICS_VIEW):
        return nopermission(request)

    num_helpers = event.helper_set.count()

    num_coordinators = event.all_coordinators.count()

    num_vegetarians = event.helper_set.filter(vegetarian=True).count()

    num_shift_slots = Shift.objects.filter(job__event=event).aggregate(
        Sum('number'))['number__sum']

    empty_slots_expr = ExpressionWrapper(F('number') - F('num_helpers'),
                                         output_field=fields.IntegerField())
    num_empty_shift_slots = Shift.objects.filter(job__event=event) \
        .annotate(num_helpers=Count('helper')) \
        .annotate(empty_slots=empty_slots_expr) \
        .aggregate(Sum('empty_slots'))['empty_slots__sum']

    total_duration = ExpressionWrapper((F('end') - F('begin')) * F('number'),
                                       output_field=fields.DurationField())
    try:
        hours_total = Shift.objects.filter(job__event=event) \
                           .annotate(duration=total_duration) \
                           .aggregate(Sum('duration'))['duration__sum']
    except (OperationalError, OverflowError):
        hours_total = None
    except Exception as e:
        # handle psycopg2.DataError without importing psycopg2
        # happens on overflow with postgresql
        if 'DataError' in str(e.__class__):
            hours_total = None
        else:
            raise e

    # render
    context = {'event': event,
               'num_helpers': num_helpers,
               'num_coordinators': num_coordinators,
               'num_vegetarians': num_vegetarians,
               'num_shift_slots': num_shift_slots,
               'num_empty_shift_slots': num_empty_shift_slots,
               'hours_total': hours_total}
    return render(request, 'statistic/overview.html', context)
