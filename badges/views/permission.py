from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from ..models import BadgeDesign, BadgePermission, BadgeRole
from ..forms import BadgeSettingsForm, BadgeDesignForm, BadgePermissionForm, \
    BadgeRoleForm, BadgeDefaultsForm, BadgeJobDefaultsForm

from registration.decorators import archived_not_available
from registration.views.utils import nopermission, is_involved
from registration.models import Event

from .utils import notactive


@login_required
@archived_not_available
def edit_permission(request, event_url_name, permission_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    permission = None
    if permission_pk:
        permission = get_object_or_404(BadgePermission, pk=permission_pk)

        # check if permission belongs to event
        if permission not in event.badge_settings.badgepermission_set.all():
            raise Http404()

    # form
    form = BadgePermissionForm(request.POST or None, instance=permission,
                               settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('badges:settings',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'badges/edit_permission.html',
                  context)
