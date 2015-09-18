from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .utils import nopermission, get_or_404, is_involved

from ..models import Event, BadgeDesign
from ..forms import BadgeDesignForm


@login_required
def badges(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    context = {'event': event}
    return render(request, 'registration/admin/badges.html', context)


@login_required
def edit_badgedesign(request, event_url_name, design_pk=None, job_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # get BadgeDesign
    design = None
    if design_pk:
        design = get_object_or_404(BadgeDesign, pk=design_pk)

    # form
    form = BadgeDesignForm(request.POST or None, request.FILES or None,
                           instance=design)

    if form.is_valid():
        new_design = form.save()

        # add to job, if newly created
        if job_pk:
            job.badge_design = new_design
            job.save()
        return HttpResponseRedirect(reverse('badges', args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgedesign.html', context)
