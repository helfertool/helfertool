from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from registration.decorators import archived_not_available
from registration.views.utils import nopermission, is_involved
from registration.models import Event

from ..forms import GiftSetForm, GiftSetDeleteForm
from ..models import GiftSet

from .utils import notactive


def _validate_gift_set(event, gift_set_pk):
    if gift_set_pk:
        gift_set = get_object_or_404(GiftSet, pk=gift_set_pk)

        # check if permission belongs to event
        if gift_set.event != event:
            raise Http404()

        return gift_set
    return None


@login_required
@archived_not_available
def edit_gift_set(request, event_url_name, gift_set_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    gift_set = _validate_gift_set(event, gift_set_pk)

    # form
    form = GiftSetForm(request.POST or None, instance=gift_set, event=event)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('gifts:list',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'gifts/edit_gift_set.html',
                  context)


@login_required
@archived_not_available
def delete_gift_set(request, event_url_name, gift_set_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    gift_set = _validate_gift_set(event, gift_set_pk)

    # form
    form = GiftSetDeleteForm(request.POST or None, instance=gift_set)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Gift set deleted: %(name)s") %
                         {'name': gift_set.name})

        # redirect to shift
        return HttpResponseRedirect(reverse('gifts:list',
                                            args=[event.url_name, ]))

    # render page
    context = {'gift_set': gift_set,
               'form': form}
    return render(request, 'gifts/delete_gift_set.html', context)
