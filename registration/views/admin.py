from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from collections import OrderedDict

from .utils import nopermission, is_involved

from ..decorators import archived_not_available
from ..forms import CreateUserForm
from ..models import Event, Shift
from ..templatetags.permissions import has_adduser_group, has_perm_group


@login_required
def admin(request, event_url_name=None):
    # check permission
    if not (is_involved(request.user, event_url_name) or
            has_perm_group(request.user)):
        return nopermission(request)

    # get event
    event = None
    if event_url_name:
        event = get_object_or_404(Event, url_name=event_url_name)

    # response
    context = {'event': event}
    return render(request, 'registration/admin/index.html', context)


@login_required
def jobs_and_shifts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # list all jobs and shifts
    context = {'event': event}
    return render(request, 'registration/admin/jobs_and_shifts.html', context)


@login_required
def add_user(request):
    # check permission
    if not (request.user.is_superuser or has_adduser_group(request.user)):
        return nopermission(request)

    # form
    form = CreateUserForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        messages.success(request, _("Added user %(username)s" %
                         {'username': user}))
        return HttpResponseRedirect(reverse('add_user'))

    context = {'form': form}
    return render(request, 'registration/admin/add_user.html', context)


@login_required
@archived_not_available
def coordinators(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    if not event.is_involved(request.user):
        return nopermission(request)

    context = {'event': event}
    return render(request, 'registration/admin/coordinators.html', context)


@login_required
@archived_not_available
def statistics(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not event.is_admin(request.user):
        return nopermission(request)

    num_helpers = event.helper_set.count()

    num_coordinators = 0
    timeline = {}
    for helper in event.helper_set.all():
        if helper.is_coordinator:
            num_coordinators += 1
        else:
            day = helper.timestamp.strftime('%Y-%m-%d')
            if day in timeline:
                timeline[day] += 1
            else:
                timeline[day] = 1

    num_vegetarians = event.helper_set.filter(vegetarian=True).count()

    num_shift_slots = Shift.objects.filter(job__event=event).aggregate(
        Sum('number'))['number__sum']

    # sum up timeline
    timeline = OrderedDict(sorted(timeline.items()))
    timeline_sum = OrderedDict()
    tmp = 0
    for day in timeline:
        tmp += timeline[day]
        timeline_sum[day] = tmp

    # render
    context = {'event': event,
               'num_helpers': num_helpers,
               'num_coordinators': num_coordinators,
               'num_vegetarians': num_vegetarians,
               'num_shift_slots': num_shift_slots,
               'timeline': timeline_sum}
    return render(request, 'registration/admin/statistics.html', context)
