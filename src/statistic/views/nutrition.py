from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.decorators import archived_not_available
from registration.models import Event, Helper
from registration.permissions import has_access, has_access_event_or_job, ACCESS_STATISTICS_VIEW

from collections import OrderedDict


class NutritionData:
    """Prepare numbers about chosen nutrition for template."""

    def __init__(self, helper_set):
        # numbers
        self.num_no_preference = helper_set.filter(nutrition=Helper.NUTRITION_NO_PREFERENCE).count()
        self.num_vegetarian = helper_set.filter(nutrition=Helper.NUTRITION_VEGETARIAN).count()
        self.num_vegan = helper_set.filter(nutrition=Helper.NUTRITION_VEGAN).count()
        self.num_other = helper_set.filter(nutrition=Helper.NUTRITION_OTHER).count()

        # helpers with "other" (we want to show the comments)
        self.helpers_other = helper_set.filter(nutrition=Helper.NUTRITION_OTHER)


@login_required
@never_cache
@archived_not_available
def nutrition(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not has_access_event_or_job(request.user, event, ACCESS_STATISTICS_VIEW):
        return nopermission(request)

    # check if nutrition is collected for this event
    if not event.ask_nutrition:
        context = {"event": event}
        return render(request, "statistic/nutrition_not_active.html", context)

    # event wide
    event_data = None
    if has_access(request.user, event, ACCESS_STATISTICS_VIEW):
        event_data = NutritionData(event.helper_set)

    # for each job
    job_data = OrderedDict()
    for job in event.job_set.all():
        # check permission for job
        if not has_access(request.user, job, ACCESS_STATISTICS_VIEW):
            continue

        job_data[job] = NutritionData(job.helpers_and_coordinators())

    # render
    context = {"event": event, "event_data": event_data, "job_data": job_data}
    return render(request, "statistic/nutrition.html", context)
