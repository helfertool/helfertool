from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from registration.decorators import archived_not_available
from registration.models import Event, Helper
from registration.views.utils import nopermission

from .forms import PrerequisiteForm, PrerequisiteDeleteForm
from .models import Prerequisite

import logging
logger = logging.getLogger("helfertool")

@login_required
@archived_not_available
def edit_prerequisite(request, event_url_name, prerequisite_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # get prerequisite, if available
    prerequisite = None
    if prerequisite:
        prerequisite = get_object_or_404(prerequisite, pk=prerequisite_pk)

    # form
    form = PrerequisiteForm(request.POST or None, instance=prerequisite, event=event)

    if form.is_valid():
        prerequisite = form.save()

        log_msg = "prerequisite created"
        if prerequisite_pk:
            log_msg = "prerequisite changed"

        logger.info(log_msg, extra={
            'user': request.user,
            'event': event,
            'prerequisite': prerequisite,
        })

        # redirect to prerequisite overview
        return redirect('prerequisites:view_prerequisites', event_url_name=event.url_name)

    # render page
    context = {'event': event,
               'prerequisite': prerequisite,
               'form': form}
    return render(request, 'prerequisites/edit_prerequisite.html', context)


@login_required
def view_prerequisites(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)
    prerequisites = Prerequisite.objects.all()

    context = {'event': event,
               'prerequisites': prerequisites}
    return render(request, 'prerequisites/view_prerequisites.html', context)


@login_required
@archived_not_available
def delete_prerequisite(request, event_url_name, prerequisite_pk):
    event = get_object_or_404(Event, url_name=event_url_name)
    prerequisite = get_object_or_404(Prerequisite, pk=prerequisite_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = PrerequisiteDeleteForm(request.POST or None, instance=prerequisite)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Prerequisite deleted: %(name)s") %
                         {'name': prerequisite.name})

        logger.info("prerequisite deleted", extra={
            'user': request.user,
            'event': event,
            'prerequisite': prerequisite,
            'prerequisite_pk': prerequisite_pk,
        })

        # redirect to prerequisite overview
        return redirect('prerequisites:view_prerequisites', event_url_name=event.url_name)

    # render page
    context = {'event': event,
               'prerequisite': prerequisite,
               'form': form}
    return render(request, 'prerequisites/delete_prerequisite.html', context)


@login_required
def view_helpers_prerequisite(request, event_url_name, prerequisite_pk):

    event = get_object_or_404(Event, url_name=event_url_name)
    prerequisite = get_object_or_404(Prerequisite, pk=prerequisite_pk)

    # find all helpers that need this prerequisite
    helpers = Helper.objects.all()\
        .filter(shifts__job__prerequisites=prerequisite)

    # render page
    context = {'event': event,
               'prerequisite': prerequisite,
               'helpers': helpers}
    return render(request, 'prerequisites/view_helpers_prerequisite.html', context)

