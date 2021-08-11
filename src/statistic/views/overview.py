from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache

from badges.models import SpecialBadges
from helfertool.utils import nopermission
from registration.decorators import archived_not_available
from registration.models import Event, Shift
from registration.permissions import has_access, ACCESS_STATISTICS_VIEW


@login_required
@never_cache
@archived_not_available
def overview(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not has_access(request.user, event, ACCESS_STATISTICS_VIEW):
        return nopermission(request)

    # get data, that we need outside of chart.js
    num_people = event.helper_set.count()
    if event.badges:
        num_people += SpecialBadges.objects.filter(event=event).aggregate(Sum('number'))['number__sum'] or 0

    num_shift_slots = Shift.objects.filter(job__event=event).aggregate(Sum('number'))['number__sum'] or 0

    # render
    context = {
        'event': event,
        'num_people': num_people,
        'num_shift_slots': num_shift_slots,
    }
    return render(request, 'statistic/overview.html', context)
