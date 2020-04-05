from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from ..models import BadgePermission
from ..forms import BadgePermissionForm, BadgePermissionDeleteForm

from registration.decorators import archived_not_available
from registration.views.utils import nopermission
from registration.models import Event
from registration.permissions import has_access, ACCESS_BADGES_EDIT

from .utils import notactive


@login_required
@archived_not_available
def edit_permission(request, event_url_name, permission_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    permission = None
    if permission_pk:
        permission = get_object_or_404(BadgePermission, pk=permission_pk,
                                       badge_settings__event=event)

    # form
    form = BadgePermissionForm(request.POST or None, instance=permission,
                               settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('badges:settings_advanced',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'badges/edit_permission.html',
                  context)


@login_required
@archived_not_available
def delete_permission(request, event_url_name, permission_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    permission = get_object_or_404(BadgePermission, pk=permission_pk,
                                   badge_settings__event=event)

    # form
    form = BadgePermissionDeleteForm(request.POST or None, instance=permission)

    if form.is_valid():
        form.delete()

        return HttpResponseRedirect(reverse('badges:settings_advanced',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'form': form,
               'permission': permission}
    return render(request, 'badges/delete_permission.html',
                  context)
