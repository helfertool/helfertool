from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from .models import Event, Job, Helper
from .forms import RegisterForm

def index(request):
    events = Event.objects.all()

    # check is user is admin
    for e in events:
        e.is_admin = e.is_admin(request.user)

    # filter events, that are not active and where user is not admin
    events = [e for e in events if e.active or e.is_admin]

    context = {'events': events}
    return render(request, 'registration/index.html', context)

def form(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.active:
        # not logged in -> show login form
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # logged in -> check permission
        elif not event.is_admin(request.user):
            context = {'event': event}
            return render(request, 'registration/nopermission.html', context)

    # handle form
    form = RegisterForm(request.POST or None, event=event)

    if form.is_valid():
        helper = form.save()
        helper.send_mail()
        return HttpResponseRedirect(reverse('registered', args=[event.url_name, helper.pk]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/form.html', context)

def registered(request, event_url_name, helper_id):
    event = get_object_or_404(Event, url_name=event_url_name)
    helper = get_object_or_404(Helper, pk=helper_id)

    context = {'event': event,
               'data': helper}
    return render(request, 'registration/registered.html', context)

@login_required
def details(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        context = {'event': event}
        return render(request, 'registration/nopermission.html', context)

    # get job, if given
    job = None
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

    # show data
    context = {'event': event, 'job': job}
    return render(request, 'registration/details.html', context)
