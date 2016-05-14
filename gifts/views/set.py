from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from registration.views.utils import nopermission, is_involved
from registration.models import Event

from ..forms import GiftSetForm
from ..models import GiftSet


def edit_gift_set(request, event_url_name, gift_set_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    # get gift_set
    gift_set = None
    if gift_set_pk:
        gift_set = get_object_or_404(GiftSet, pk=gift_set_pk)

        # check if permission belongs to event
        if gift_set.event != event:
            raise Http404()

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
