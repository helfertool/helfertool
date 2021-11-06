from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission

from ..decorators import archived_not_available
from ..forms import MergeDuplicatesForm
from ..models import Event
from ..permissions import has_access, ACCESS_EVENT_EDIT_DUPLICATES

from collections import OrderedDict

import logging
logger = logging.getLogger("helfertool.registration")


@login_required
@never_cache
@archived_not_available
def duplicates(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT_DUPLICATES):
        return nopermission(request)

    duplicates = event.helper_set.annotate(email_lower=Lower('email')).values('email_lower') \
        .annotate(email_count=Count('email_lower')).exclude(email_count=1).order_by('email_lower')

    duplicated_helpers = OrderedDict()

    for dup in duplicates:
        duplicated_helpers[dup['email_lower']] = event.helper_set.filter(email__iexact=dup['email_lower'])

    # overview over jobs
    context = {'event': event,
               'duplicated_helpers': duplicated_helpers}
    return render(request, 'registration/admin/duplicates.html', context)


@login_required
@never_cache
@archived_not_available
def merge(request, event_url_name, email):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT_DUPLICATES):
        return nopermission(request)

    helpers = event.helper_set.filter(email__iexact=email)

    form = None
    error = False

    if helpers.count() > 1:
        form = MergeDuplicatesForm(request.POST or None, helpers=helpers)

        if form.is_valid():
            try:
                h = form.merge()

                logger.info("helper merged", extra={
                    'user': request.user,
                    'helper': h,
                    'event': event,
                })

                return redirect('view_helper', event_url_name=event_url_name, helper_pk=h.pk)
            except ValueError:
                # happens only if the shifts changed between is_valid() and merge()
                error = True

    context = {'event': event,
               'form': form,
               'error': error}
    return render(request, 'registration/admin/merge.html', context)
