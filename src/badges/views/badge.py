from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from helfertool.utils import serve_file, nopermission
from registration.permissions import has_access, ACCESS_BADGES_EDIT_HELPER
from registration.utils import get_or_404

from ..forms import BadgeForm
from .utils import notactive


@login_required
@never_cache
def edit_badge(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT_HELPER):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    form = BadgeForm(request.POST or None, request.FILES or None,
                     instance=helper.badge)

    if form.is_valid():
        form.save()

        return redirect('view_helper', event_url_name=event_url_name, helper_pk=helper.pk)

    # render page
    context = {'event': event,
               'helper': helper,
               'form': form}
    return render(request, 'badges/edit_badge.html', context)


@login_required
@never_cache
def get_badge_photo(request, event_url_name, helper_pk):
    """ Download badge photo of normal badge.

    For special badges: get_specialbadges_photo """
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT_HELPER):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    return serve_file(helper.badge.photo)
