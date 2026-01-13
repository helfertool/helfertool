from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from news.helper import news_validate_helper

from ..utils import get_or_404
from ..forms import RegisterForm, DeregisterForm, HelperForm
from ..models import Event, Link
from ..permissions import has_access, ACCESS_INVOLVED

import datetime
from collections import OrderedDict
from itertools import groupby

import logging

logger = logging.getLogger("helfertool.registration")


def index_all_events(request):
    return index(request, False)


def index(request, filter_old_events=True):
    events = Event.objects.all()

    # public events, sorted by date
    active_events = sorted([e for e in events if e.active], key=lambda e: e.date)

    # only one public event and it is active -> redirect
    if events.count() == 1 and active_events:
        return redirect("form", event_url_name=active_events[0].url_name)

    # if user is authenticated, mark events as involved or not involved
    # usually, we should use has_access to verify access. but this is too slow for many events with many jobs
    # so we do it manually here...
    inactive_events_by_year = []
    enable_show_more_events = False
    if not request.user.is_anonymous:
        # get all involved events based on role assignments
        # add the "involved" flag - it will be used by the template
        all_involved_events = Event.objects.filter(Q(admins=request.user) | Q(job__job_admins=request.user)).distinct()
        for e in events:
            e.involved = request.user.is_superuser or e in all_involved_events

        # get all events, that should be listed in the inactive section
        # if we are superuser, thats all inactive events. otherwise, only the involved, inactive ones
        if request.user.is_superuser:
            inactive_events = events.filter(active=False)
        else:
            inactive_events = all_involved_events.filter(active=False)

        # and then optionally cut away the old ones
        if filter_old_events:
            inactive_events_last_years = []
            oldest_year = datetime.datetime.now().year - settings.EVENTS_LAST_YEARS
            for event in inactive_events:
                if event.date.year >= oldest_year:
                    inactive_events_last_years.append(event)
                else:
                    # we skip an event, so we need a button to show it
                    enable_show_more_events = True

            inactive_events = inactive_events_last_years

        # group inactive_events by date
        # first, sort descending by date
        inactive_events_sorted = sorted(inactive_events, key=lambda e: e.date, reverse=True)
        # then group by year
        inactive_events_grouped = groupby(inactive_events_sorted, key=lambda e: e.date.year)
        # then convert to data structure that django templates understand and sort by name
        inactive_events_by_year = OrderedDict()
        for year, events in inactive_events_grouped:
            inactive_events_by_year[year] = list(sorted(events, key=lambda e: e.name.lower()))

    context = {
        "active_events": active_events,
        "inactive_events_by_year": inactive_events_by_year,
        "enable_show_more_events": enable_show_more_events,
    }
    return render(request, "registration/index.html", context)


@never_cache
def form(request, event_url_name, link_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # get link if given
    link = None
    shifts_qs = None
    if link_pk:
        try:
            link = Link.objects.get(pk=link_pk)
            shifts_qs = link.shifts.all()
        except (Link.DoesNotExist, ValidationError):
            # show some message when link does not exist
            context = {"event": event}
            return render(request, "registration/invalid_link.html", context)

        # check if link belongs to event
        if link.event != event:
            raise Http404()

    # check permission
    user_is_involved = has_access(request.user, event, ACCESS_INVOLVED)
    if not event.active and not link:
        # not logged in -> show message
        if not request.user.is_authenticated:
            # show some message when link does not exist
            context = {"event": event}
            return render(request, "registration/not_active.html", context)
        # logged in -> check permission
        elif not user_is_involved:
            return nopermission(request)

    # handle form
    form = RegisterForm(request.POST or None, event=event, shifts_qs=shifts_qs, is_link=link is not None)

    if form.is_valid():
        helper = form.save()

        logger.info(
            "helper registered",
            extra={
                "event": event,
                "helper": helper,
                "withlink": link_pk is not None,
            },
        )

        if not helper.send_mail(request, internal=False):
            messages.error(request, _("Sending the mail failed, but the registration was saved."))

        return redirect("registered", event_url_name=event.url_name, helper_pk=helper.pk)

    context = {
        "event": event,
        "form": form,
        "user_is_involved": user_is_involved,
        "link": link,
    }
    return render(request, "registration/form.html", context)


@never_cache
def registered(request, event_url_name, helper_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk, handle_duplicates=True)

    context = {"event": event, "data": helper}
    return render(request, "registration/registered.html", context)


@never_cache
def validate(request, event_url_name, helper_pk, validation_id=None):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk, handle_duplicates=True)

    # the validation_id should prevent that users guess the url of this page
    # for now, we accept links without this ID, but future releases will require it
    if validation_id and helper.validation_id != validation_id:
        raise Http404

    if not helper.validated:
        helper.validated = True
        helper.timestamp_validated = timezone.now()
        helper.save()

        logger.info(
            "helper validated",
            extra={
                "event": event,
                "helper": helper,
            },
        )

        # also validate newsletter subscription, if necessary
        news_validate_helper(helper)

    context = {"event": event, "helper": helper}
    return render(request, "registration/validate.html", context)


@never_cache
def deregister(request, event_url_name, helper_pk, shift_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk, shift_pk=shift_pk)

    if not event.changes_possible:
        context = {"event": event}
        return render(request, "registration/changes_not_possible.html", context)

    form = DeregisterForm(request.POST or None, instance=helper, shift=shift)

    if form.is_valid():
        form.delete()

        logger.info(
            "helper deregistered",
            extra={
                "event": event,
                "helper": helper,
            },
        )

        if not helper.pk:
            return redirect("deleted", event_url_name=event.url_name)

        return redirect("registered", event_url_name=event.url_name, helper_pk=helper.pk)

    context = {"event": event, "helper": helper, "shift": shift, "form": form}
    return render(request, "registration/deregister.html", context)


@never_cache
def deleted(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    context = {"event": event}
    return render(request, "registration/deleted.html", context)


@never_cache
def update_personal(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    if not event.changes_possible:
        context = {"event": event}
        return render(request, "registration/changes_not_possible.html", context)

    form = HelperForm(request.POST or None, instance=helper, event=event, public=True, mask_sensitive=True)

    if form.is_valid():
        form.save()

        logger.info(
            "helper dataupdated",
            extra={
                "event": event,
                "helper": helper,
            },
        )

        if form.email_has_changed:
            if not helper.send_mail(request, internal=False):
                messages.error(request, _("Sending the mail failed, but the change was saved."))

        return redirect("registered", event_url_name=event.url_name, helper_pk=helper.pk)

    context = {"event": event, "data": helper, "personal_data_form": form}
    return render(request, "registration/registered.html", context)
