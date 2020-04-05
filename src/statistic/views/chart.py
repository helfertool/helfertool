from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from registration.decorators import archived_not_available
from registration.models import Event
from registration.views.utils import nopermission
from registration.permissions import has_access, ACCESS_STATISTICS_VIEW


@login_required
@archived_not_available
def chart_timeline(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not has_access(request.user, event, ACCESS_STATISTICS_VIEW):
        return JsonResponse({})

    # collect data
    timeline = {}
    for helper in event.helper_set.all():
        if not helper.is_coordinator:
            day = helper.timestamp.strftime('%Y-%m-%d')
            if day in timeline:
                timeline[day] += 1
            else:
                timeline[day] = 1

    # abort if no data found
    if len(timeline) == 0:
        return JsonResponse({})

    # sum up timeline
    timeline_sum_data = []

    days = sorted(timeline.keys())
    cur_sum = 0
    for day in days:
        cur_sum += timeline[day]

        timeline_sum_data.append({
            "x": day,
            "y": cur_sum,
        })

    # output format
    output = {
        "type": "line",
        "data": {
            'datasets': [
                {
                    "label": _("Number of helpers"),
                    "data": timeline_sum_data,
                    "lineTension": 0.2,
                },
            ]
        },
        "options": {
            "scales": {
                "xAxes": [{
                    "type": 'time',
                }],
            },
        },
    }

    return JsonResponse(output)
