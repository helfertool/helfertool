from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _

from smtplib import SMTPException

from .utils import nopermission, get_or_404

from ..forms import RegisterForm, DeregisterForm, HelperForm
from ..models import Event, Link

from news.helper import news_test_email


def index(request):
    events = Event.objects.all()

    # check is user is admin
    for e in events:
        e.involved = e.is_involved(request.user)

    # filter events, that are not active and where user is not admin
    active_events = [e for e in events if e.active]
    involved_events = [e for e in events if not e.active and e.involved]

    # only one public event and no internal events -> redirect always
    # but no redirect for logged in users when multiple events exist
    if len(active_events) == 1 and \
            (len(involved_events) == 0 and
             not request.user.is_authenticated()):
        return redirect(form, event_url_name=active_events[0].url_name)

    context = {'active_events': active_events,
               'involved_events': involved_events}
    return render(request, 'registration/index.html', context)


def form(request, event_url_name, link_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # get link if given
    link = None
    all_shifts = None
    if link_pk:
        try:
            link = Link.objects.get(pk=link_pk)
            all_shifts = link.shifts.all()
        except (Link.DoesNotExist, ValueError):
            # show some message when link does not exist
            context = {'event': event}
            return render(request, 'registration/invalid_link.html', context)

        # check if link belongs to event
        if link.event != event:
            raise Http404()

    # check permission
    if not event.active and not link:
        # not logged in -> show message
        if not request.user.is_authenticated():
            # show some message when link does not exist
            context = {'event': event}
            return render(request, 'registration/not_active.html', context)
        # logged in -> check permission
        elif not event.is_involved(request.user):
            return nopermission(request)

    # handle form
    form = RegisterForm(request.POST or None, event=event, shifts=all_shifts,
                        link=link is not None)

    if form.is_valid():
        helper = form.save()

        try:
            helper.send_mail(request, internal=False)
        except SMTPException:
            messages.error(request, _("Sending the mail failed, but the "
                                      "registration was saved."))
        return HttpResponseRedirect(reverse('registered',
                                            args=[event.url_name, helper.pk]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/form.html', context)


def registered(request, event_url_name, helper_id=None):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_id)

    news = news_test_email(helper.email)

    context = {'event': event,
               'data': helper,
               'news': news}
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


def deregister(request, event_url_name, helper_id, shift_pk):
    event, job, shift, helper = get_or_404(event_url_name,
                                           helper_pk=helper_id,
                                           shift_pk=shift_pk)

    if not event.changes_possible:
        context = {'event': event}
        return render(request, 'registration/changes_not_possible.html',
                      context)

    form = DeregisterForm(request.POST or None, instance=helper, shift=shift)

    if form.is_valid():
        form.delete()

        if not helper.pk:
            return HttpResponseRedirect(reverse('deleted',
                                                args=[event.url_name]))

        return HttpResponseRedirect(reverse('registered',
                                            args=[event.url_name, helper.pk]))

    context = {'event': event,
               'helper': helper,
               'shift': shift,
               'form': form}
    return render(request, 'registration/deregister.html', context)


def deleted(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    context = {'event': event}
    return render(request, 'registration/deleted.html', context)


def update_personal(request, event_url_name, helper_id):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_id)

    if not event.changes_possible:
        context = {'event': event}
        return render(request, 'registration/changes_not_possible.html',
                      context)

    form = HelperForm(request.POST or None, instance=helper, event=event,
                      public=True)

    if form.is_valid():
        form.save(request=request)

        return HttpResponseRedirect(reverse('registered',
                                            args=[event.url_name, helper.pk]))

    news = news_test_email(helper.email)  # needed in template

    context = {'event': event,
               'data': helper,
               'news': news,
               'personal_data_form': form}
    return render(request, 'registration/registered.html', context)
