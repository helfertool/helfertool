from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from .utils import nopermission

from ..models import Event, Link
from ..forms import LinkForm, LinkDeleteForm
from ..decorators import archived_not_available
from ..permissions import has_access, ACCESS_EVENT_EDIT_LINKS

import logging
logger = logging.getLogger("helfertool")


@login_required
def links(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT_LINKS):
        return nopermission(request)

    # get all links
    links = event.link_set.all()

    context = {'event': event,
               'links': links}
    return render(request, 'registration/admin/links.html', context)


@login_required
@archived_not_available
def edit_link(request, event_url_name, link_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT_LINKS):
        return nopermission(request)

    # get job, if available
    link = None
    if link_pk:
        link = get_object_or_404(Link, pk=link_pk)

        if event != link.event:
            raise Http404()

    # form
    form = LinkForm(request.POST or None, instance=link, event=event,
                    creator=request.user)

    if form.is_valid():
        link = form.save()

        log_msg = "link created"
        if link_pk:
            log_msg = "link changed"
        logger.info(log_msg, extra={
            'user': request.user,
            'event': event,
            'link': link.id,
        })

        return HttpResponseRedirect(reverse('links', args=[event_url_name]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_link.html', context)


@login_required
@archived_not_available
def delete_link(request, event_url_name, link_pk):
    event = get_object_or_404(Event, url_name=event_url_name)
    link = get_object_or_404(Link, pk=link_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT_LINKS):
        return nopermission(request)

    # check if event matches
    if event != link.event:
        raise Http404()

    # form
    form = LinkDeleteForm(request.POST or None, instance=link)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Link deleted"))

        logger.info("link deleted", extra={
            'user': request.user,
            'event': event,
            'link': link_pk,
        })

        # redirect to shift
        return HttpResponseRedirect(reverse('links', args=[event_url_name]))

    # render page
    context = {'event': event,
               'link': link,
               'form': form}
    return render(request, 'registration/admin/delete_link.html', context)
