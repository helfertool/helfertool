from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from collections import OrderedDict

from .utils import nopermission, is_involved

from ..models import Event, Helper
from ..forms import UserCreationForm
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
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        messages.success(request, _("Added user %(username)s" %
                         {'username': user}))
        return HttpResponseRedirect(reverse('add_user'))

    context = {'form': form}
    return render(request, 'registration/admin/add_user.html', context)


@login_required
def coordinators(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    if not event.is_involved(request.user):
        return nopermission(request)

    context = {'event': event}
    return render(request, 'registration/admin/coordinators.html', context)


@login_required
def shirts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # shirt sizes for helpers
    helper_shirts = event.helper_set.values('shirt').annotate(num=Count('shirt'))

    # create data for template (iterate over all sizes in correct order)
    shirts = OrderedDict()
    for size, name in Helper.SHIRT_CHOICES:
        num = 0

        # get size for helpers
        try:
            num = helper_shirts.get(shirt=size)['num']
        except Helper.DoesNotExist:
            pass

        shirts.update({name: num})

    # render
    context = {'event': event,
               'shirts': shirts}
    return render(request, 'registration/admin/shirts.html', context)
