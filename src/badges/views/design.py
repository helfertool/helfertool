from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from helfertool.utils import serve_file
from registration.decorators import archived_not_available
from registration.models import Event
from registration.views.utils import nopermission
from registration.permissions import has_access, ACCESS_BADGES_EDIT

from .utils import notactive
from ..models import BadgeDesign
from ..forms import BadgeDesignForm, BadgeDesignDeleteForm


@login_required
@archived_not_available
def edit_design(request, event_url_name, design_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgeDesign
    design = None
    if design_pk:
        design = get_object_or_404(BadgeDesign, pk=design_pk, badge_settings__event=event)

    # form
    form = BadgeDesignForm(request.POST or None, request.FILES or None,
                           instance=design, settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('badges:settings', args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'badges/edit_design.html', context)


@login_required
@archived_not_available
def delete_design(request, event_url_name, design_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    design = get_object_or_404(BadgeDesign, pk=design_pk, badge_settings__event=event)

    # form
    form = BadgeDesignDeleteForm(request.POST or None, instance=design)

    if form.is_valid():
        form.delete()

        return HttpResponseRedirect(reverse('badges:settings', args=[event.url_name, ]))

    context = {'event': event,
               'form': form,
               'design': design}
    return render(request, 'badges/delete_design.html', context)


@login_required
@archived_not_available
def get_design_bg(request, event_url_name, design_pk, side):
    if side not in ["front", "back"]:
        raise Http404()

    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgeDesign
    design = get_object_or_404(BadgeDesign, pk=design_pk, badge_settings__event=event)

    # output
    if side == "front":
        return serve_file(design.bg_front)
    else:
        return serve_file(design.bg_back)
