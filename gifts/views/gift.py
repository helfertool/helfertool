from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from registration.views.utils import nopermission, is_involved
from registration.models import Event

from ..forms import GiftForm, GiftDeleteForm
from ..models import Gift, GiftSet

from .utils import notactive


def _validate_gift(event, gift_pk):
    # get gift
    if gift_pk:
        gift = get_object_or_404(Gift, pk=gift_pk)

        # check if permission belongs to event
        if gift.event != event:
            raise Http404()

        return gift
    return None


@login_required
def edit_gift(request, event_url_name, gift_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    gift = _validate_gift(event, gift_pk)

    # form
    form = GiftForm(request.POST or None, instance=gift, event=event)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('gifts:list',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'gifts/edit_gift.html',
                  context)


@login_required
def delete_gift(request, event_url_name, gift_pk):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    gift = _validate_gift(event, gift_pk)

    # gift sets that use this gift
    gift_sets = GiftSet.objects.filter(gifts__id=gift.id).all()

    # form
    form = GiftDeleteForm(request.POST or None, instance=gift)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Gift deleted: %(name)s") %
                         {'name': gift.name})

        # redirect to shift
        return HttpResponseRedirect(reverse('gifts:list',
                                            args=[event.url_name, ]))

    # render page
    context = {'gift': gift,
               'gift_sets': gift_sets,
               'form': form}
    return render(request, 'gifts/delete_gift.html', context)
