from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from registration.decorators import archived_not_available
from registration.views.utils import nopermission
from registration.models import Event
from registration.permissions import has_access, ACCESS_GIFTS_EDIT

from ..forms import GiftSetForm, GiftSetDeleteForm
from ..models import GiftSet

from .utils import notactive

import logging
logger = logging.getLogger("helfertool")


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
    if not has_access(request.user, event, ACCESS_GIFTS_EDIT):
        return nopermission(request)

    # check if active
    if not event.gifts:
        return notactive(request)

    gift_set = _validate_gift_set(event, gift_set_pk)

    # form
    form = GiftSetForm(request.POST or None, instance=gift_set, event=event)

    if form.is_valid():
        gift_set = form.save()

        log_msg = "giftset created"
        if gift_set_pk:
            log_msg = "giftset changed"
        logger.info(log_msg, extra={
            'user': request.user,
            'event': event,
            'giftset_pk': gift_set.pk,
            'giftset': gift_set.name,
        })

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
    if not has_access(request.user, event, ACCESS_GIFTS_EDIT):
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

        logger.info("giftset deleted", extra={
            'user': request.user,
            'event': event,
            'giftset_pk': gift_set_pk,
            'giftset': gift_set.name,
        })

        # redirect to shift
        return HttpResponseRedirect(reverse('gifts:list',
                                            args=[event.url_name, ]))

    # render page
    context = {'gift_set': gift_set,
               'form': form,
               'event': event}
    return render(request, 'gifts/delete_gift_set.html', context)
