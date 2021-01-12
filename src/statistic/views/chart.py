from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from datetime import timedelta
from itertools import cycle

from badges.models import SpecialBadges
from registration.decorators import archived_not_available
from registration.models import Event, Shift, HelperShift
from registration.permissions import has_access, ACCESS_STATISTICS_VIEW

# colors
# TODO: get from theming config, if this is implemented
colors_primary = [
    "#1a876e",
    "#29d3ac",
    "#31ffd0",
]

colors_danger = [
    "#d53e54",
    "#d53e54",
    "#d5939d",
]


def _chart_doughnut(data):
    """
    Return JSON for chart.js doughnut char.

    data = [
        {
            "value": 10,
            "labal": "Test",
            "danger": False,  # optional
        },
        ...
    ]
    """
    # colors:
    primary = cycle(colors_primary)
    danger = cycle(colors_danger)

    # prepare data for chart.js
    values = [d["value"] for d in data]
    labels = [d["label"] for d in data]

    colors = []
    for d in data:
        if d.get("danger", False):
            colors.append(next(danger))
        else:
            colors.append(next(primary))

    # json for chart.js
    output = {
        "type": "doughnut",
        "data": {
            "datasets": [
                {
                    "data": values,
                    "backgroundColor": colors,
                },
            ],
            "labels": labels
        },
        "options": {
            "cutout": "60%",
        }
    }

    return JsonResponse(output)


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

    # add "0" value on day before first registration
    day_one = event.helper_set.order_by("timestamp").first().timestamp
    day_zero = day_one - timedelta(days=1)
    timeline[day_zero.strftime('%Y-%m-%d')] = 0

    # sum up the days
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
                    "borderColor": colors_primary[0],
                    "lineTension": 0.3,
                },
            ]
        },
        "options": {
            "scales": {
                "x": {
                    "type": "time",
                },
                "y": {
                    "ticks": {
                        "precision": 0,
                    }
                },
            },
            "plugins": {
                "legend": {
                    "display": False,
                }
            },
            "maintainAspectRatio": False,
        },
    }

    return JsonResponse(output)


@login_required
@archived_not_available
def chart_helpers(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not has_access(request.user, event, ACCESS_STATISTICS_VIEW):
        return JsonResponse({})

    # get data
    total_helpers = event.helper_set.count()

    num_coordinators = event.all_coordinators.count()
    num_helpers = total_helpers - num_coordinators

    if event.badges:
        num_specialbadges = SpecialBadges.objects.filter(event=event).aggregate(Sum('number'))['number__sum'] or 0
    else:
        num_specialbadges = 0

    # output format
    data = [
        {"value": num_helpers, "label": _("Helpers")},
        {"value": num_coordinators, "label": _("Coordinators")},
    ]
    if num_coordinators:
        data.append({"value": num_specialbadges, "label": _("Special badges")})

    return _chart_doughnut(data)


@login_required
@archived_not_available
def chart_shifts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not has_access(request.user, event, ACCESS_STATISTICS_VIEW):
        return JsonResponse({})

    # get data
    total_shifts = Shift.objects.filter(job__event=event).aggregate(Sum('number'))['number__sum']
    filled_shifts = HelperShift.objects.filter(helper__event=event).count()
    vacant_shifts = total_shifts - filled_shifts

    # output format
    data = [
        {"value": filled_shifts, "label": _("Filled slots")},
        {"value": vacant_shifts, "label": _("Vacant slots"), "danger": True},
    ]

    return _chart_doughnut(data)


@login_required
@archived_not_available
def chart_eating_habits(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not has_access(request.user, event, ACCESS_STATISTICS_VIEW):
        return JsonResponse({})

    if not event.ask_vegetarian:
        JsonResponse({})

    # get data
    num_vegetarians = event.helper_set.filter(vegetarian=True).count()
    num_rest = event.helper_set.filter(vegetarian=False).count()

    # output format
    data = [
        {"value": num_vegetarians, "label": _("Vegetarian")},
        {"value": num_rest, "label": _("No preference")},
    ]

    return _chart_doughnut(data)
