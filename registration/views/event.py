from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from .utils import is_admin, nopermission

from ..models import Event
from ..forms import EventForm, EventDeleteForm
from ..templatetags.permissions import has_addevent_group


@login_required
def edit_event(request, event_url_name=None):
    # TODO shorten
    # check permission
    if event_url_name:
        # event exists -> superuser or admin
        if not is_admin(request.user, event_url_name):
            return nopermission(request)
    else:
        # event will be created -> superuser or addevent group
        if not (request.user.is_superuser or has_addevent_group(request.user)):
            return nopermission(request)

    # get event
    event = None
    if event_url_name:
        event = get_object_or_404(Event, url_name=event_url_name)

    # handle form
    form = EventForm(request.POST or None, request.FILES or None,
                     instance=event)

    if form.is_valid():
        event = form.save()

        if not event_url_name:
            messages.success(request, _("Event was created: %(event)s") %
                             {'event': event.name})

        # redirect to this page, so reload does not send the form data again
        # if the event was created, this redirects to the event settings
        return HttpResponseRedirect(reverse('edit_event',
                                            args=[form['url_name'].value()]))

    # get event without possible invalid modifications from form
    saved_event = None
    if event_url_name:
        saved_event = get_object_or_404(Event, url_name=event_url_name)

    # render page
    context = {'event': saved_event,
               'form': form}
    return render(request, 'registration/admin/edit_event.html', context)


@login_required
def delete_event(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = EventDeleteForm(request.POST or None, instance=event)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Event deleted: %(name)s") %
                         {'name': event.name})

        # redirect to shift
        return HttpResponseRedirect(reverse('index'))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/delete_event.html', context)
