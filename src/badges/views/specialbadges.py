from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission, serve_file
from registration.decorators import archived_not_available
from registration.models import Event
from registration.permissions import has_access, ACCESS_BADGES_EDIT_SPECIAL

from ..forms import SpecialBadgesForm, BadgeForm, SpecialBadgesDeleteForm
from ..models import SpecialBadges
from .utils import notactive


@login_required
@never_cache
def list_specialbadges(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT_SPECIAL):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get special badges (=badges without helper object)
    specialbadges = SpecialBadges.objects.filter(event=event)

    context = {"event": event, "specialbadges": specialbadges}
    return render(request, "badges/list_specialbadges.html", context)


@login_required
@never_cache
@archived_not_available
def edit_specialbadges(request, event_url_name, specialbadges_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT_SPECIAL):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get special badges
    specialbadges = None
    if specialbadges_pk:
        specialbadges = get_object_or_404(SpecialBadges, pk=specialbadges_pk, event=event)

    # form
    form = SpecialBadgesForm(request.POST or None, instance=specialbadges, event=event)

    if form.is_valid():
        instance = form.save()

        return redirect(
            "badges:edit_specialbadges_template", event_url_name=event.url_name, specialbadges_pk=instance.pk
        )

    context = {"event": event, "form": form}
    return render(request, "badges/edit_specialbadges.html", context)


@login_required
@never_cache
@archived_not_available
def edit_specialbadges_template(request, event_url_name, specialbadges_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT_SPECIAL):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get special badges
    specialbadges = get_object_or_404(SpecialBadges, pk=specialbadges_pk, event=event)

    # form
    form = BadgeForm(request.POST or None, request.FILES or None, instance=specialbadges.template_badge)

    if form.is_valid():
        form.save()
        specialbadges.save()  # sync changes to other badges

        return redirect("badges:list_specialbadges", event_url_name=event.url_name)

    context = {"event": event, "form": form}
    return render(request, "badges/edit_badge.html", context)


@login_required
@never_cache
@archived_not_available
def delete_specialbadges(request, event_url_name, specialbadges_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT_SPECIAL):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get special badges
    specialbadges = get_object_or_404(SpecialBadges, pk=specialbadges_pk, event=event)

    form = SpecialBadgesDeleteForm(request.POST or None, instance=specialbadges)

    if form.is_valid():
        form.delete()

        return redirect("badges:list_specialbadges", event_url_name=event.url_name)

    context = {"event": event, "form": form, "specialbadges": specialbadges}
    return render(request, "badges/delete_specialbadges.html", context)


@login_required
@never_cache
def get_specialbadges_photo(request, event_url_name, specialbadges_pk):
    """Download badge photo of special badge.

    For normal badge: get_badge_photo"""
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT_SPECIAL):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get special badges
    specialbadges = get_object_or_404(SpecialBadges, template_badge=specialbadges_pk, event=event)

    return serve_file(specialbadges.template_badge.photo)
