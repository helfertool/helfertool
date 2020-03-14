from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms import BadgeForm

from registration.views.utils import nopermission, get_or_404
from registration.permissions import has_access, ACCESS_BADGES_EDIT_HELPER

from .utils import notactive


@login_required
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

        return HttpResponseRedirect(reverse('view_helper',
                                            args=[event_url_name, helper.pk]))

    # render page
    context = {'event': event,
               'helper': helper,
               'form': form}
    return render(request, 'badges/edit_badge.html', context)
