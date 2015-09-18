from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect

from .utils import nopermission, get_or_404

from ..models import Event, Link
from ..forms import RegisterForm


def index(request):
    events = Event.objects.all()

    # check is user is admin
    for e in events:
        e.involved = e.is_involved(request.user)

    # filter events, that are not active and where user is not admin
    active_events = [e for e in events if e.active]
    involved_events = [e for e in events if not e.active and e.involved]

    context = {'active_events': active_events,
               'involved_events': involved_events}
    return render(request, 'registration/index.html', context)


def form(request, event_url_name, link_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # get link if given
    link = None
    if link_pk:
        try:
            link = Link.objects.get(pk=link_pk)
        except Link.DoesNotExist as e:
            # show some message when link does not exist
            context = {'event': event}
            return render(request, 'registration/invalid_link.html', context)

        # check if link belongs to event
        if link.event != event:
            raise Http404()

    # check permission
    if not event.active and not link:
        # not logged in -> show login form
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # logged in -> check permission
        elif not event.is_involved(request.user):
            return nopermission(request)

    # handle form
    form = RegisterForm(request.POST or None, event=event, link=link)

    if form.is_valid():
        helper = form.save()

        # if mail validation if necessary: helper is not validated
        if event.mail_validation:
            helper.validated = False
            helper.save()

        helper.send_mail(request)
        return HttpResponseRedirect(reverse('registered',
                                            args=[event.url_name, helper.pk]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/form.html', context)


def registered(request, event_url_name, helper_id):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_id)

    context = {'event': event,
               'data': helper}
    return render(request, 'registration/registered.html', context)


def validate(request, event_url_name, helper_id):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_id)

    # 404 if validation is not used
    if not event.mail_validation:
        raise Http404()

    # already validated?
    already_validated = helper.validated

    # validate
    helper.validated = True
    helper.save()

    context = {'event': event,
               'already_validated': already_validated}
    return render(request, 'registration/validate.html', context)
