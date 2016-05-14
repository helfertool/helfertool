from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from registration.views.utils import nopermission, is_involved
from registration.models import Event

from ..forms import GiftForm
from ..models import Gift


def edit_gift(request, event_url_name, gift_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    # get gift
    gift = None
    if gift_pk:
        gift = get_object_or_404(Gift, pk=gift_pk)

        # check if permission belongs to event
        if gift.event != event:
            raise Http404()

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
