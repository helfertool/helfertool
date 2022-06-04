from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from registration.decorators import archived_not_available
from registration.models import Event
from registration.permissions import has_access, ACCESS_BADGES_EDIT

from ..forms import BadgeRoleForm, BadgeRoleDeleteForm
from ..models import BadgeRole
from .utils import notactive


@login_required
@never_cache
@archived_not_available
def edit_role(request, event_url_name, role_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    role = None
    if role_pk:
        role = get_object_or_404(BadgeRole, pk=role_pk, badge_settings__event=event)

    # form
    form = BadgeRoleForm(request.POST or None, instance=role, settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return redirect("badges:settings", event_url_name=event.url_name)

    context = {"event": event, "form": form}
    return render(request, "badges/edit_role.html", context)


@login_required
@never_cache
@archived_not_available
def delete_role(request, event_url_name, role_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    role = get_object_or_404(BadgeRole, pk=role_pk, badge_settings__event=event)

    form = BadgeRoleDeleteForm(request.POST or None, instance=role)

    if form.is_valid():
        form.delete()

        return redirect("badges:settings", event_url_name=event.url_name)

    context = {"event": event, "form": form, "role": role}
    return render(request, "badges/delete_role.html", context)
