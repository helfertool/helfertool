from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.permissions import has_access, ACCESS_CORONA_VIEW, ACCESS_CORONA_EDIT
from registration.utils import get_or_404

from ..forms import ContactTracingDataForm
from ..models import ContactTracingData
from .utils import notactive

import logging
logger = logging.getLogger("helfertool.corona")


@login_required
@never_cache
def view_helper(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permissions
    if not has_access(request.user, helper, ACCESS_CORONA_VIEW):
        return nopermission(request)

    # check if corona contact tracing is active
    if not event.corona:
        return notactive(request)

    # get data if it exists
    try:
        data = helper.contacttracingdata
    except ContactTracingData.DoesNotExist:
        data = None

    # render page
    context = {'event': event,
               'helper': helper,
               'data': data}
    return render(request, 'corona/view_helper.html', context)


@login_required
@never_cache
def edit_helper(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permissions
    if not has_access(request.user, helper, ACCESS_CORONA_EDIT):
        return nopermission(request)

    # check if corona contact tracing is active
    if not event.corona:
        return notactive(request)

    # get data if it exists
    try:
        data = helper.contacttracingdata
    except ContactTracingData.DoesNotExist:
        data = None

    # form
    form = ContactTracingDataForm(request.POST or None, instance=data, event=event)
    if form.is_valid():
        form.save(helper=helper)

        logger.info("helper coronadata", extra={
            'user': request.user,
            'event': event,
            'helper': helper,
        })

        return redirect('corona:view_helper', event_url_name=event_url_name, helper_pk=helper.pk)

    # render page
    context = {'event': event,
               'helper': helper,
               'form': form}
    return render(request, 'corona/edit_helper.html', context)
