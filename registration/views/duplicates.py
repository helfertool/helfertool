from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

from collections import OrderedDict

from .utils import nopermission

from ..models import Event


@login_required
def duplicates(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    duplicates = event.helper_set.values('email').annotate(
        email_count=Count('email')).exclude(email_count=1).order_by('email')

    duplicated_helpers = OrderedDict()

    for dup in duplicates:
        duplicated_helpers[dup['email']] = event.helper_set.filter(
            email=dup['email'])

    # overview over jobs
    context = {'event': event,
               'duplicated_helpers': duplicated_helpers}
    return render(request, 'registration/admin/duplicates.html', context)
