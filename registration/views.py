from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from io import BytesIO

from .models import Event, Job, Helper
from .forms import RegisterForm
from .utils import escape_filename
from .export import xlsx

def index(request):
    events = Event.objects.all()

    # check is user is admin
    for e in events:
        e.is_admin = e.is_admin(request.user)

    # filter events, that are not active and where user is not admin
    active_events = [e for e in events if e.active]
    administered_events = [e for e in events if not  e.active and e.is_admin]

    context = {'active_events': active_events,
               'administered_events': administered_events}
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
            return render(request, 'registration/admin/nopermission.html', context)

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
def admin(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        context = {'event': event}
        return render(request, 'registration/admin/nopermission.html', context)

    context = {'event': event}
    return render(request, 'registration/admin/index.html', context)


@login_required
def helpers(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        context = {'event': event}
        return render(request, 'registration/admin/nopermission.html', context)

    # helpers of one job
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)
        context = {'event': event, 'job': job}
        return render(request, 'registration/admin/helpers-job.html', context)

    # overview over jobs
    context = {'event': event}
    return render(request, 'registration/admin/helpers.html', context)

@login_required
def excel(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        context = {'event': event}
        return render(request, 'registration/admin/nopermission.html', context)

    # list of jobs for export
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)
        jobs = [job, ]
        filename = "%s - %s" % (event.name, job.name)
    else:
        jobs = Job.objects.all()
        filename = event.name

    # start http response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % escape_filename(filename)

    # create buffer
    buffer = BytesIO()

    # create xlsx sheets
    xlsx(buffer, jobs)

    # close buffer, send file
    data = buffer.getvalue()
    buffer.close()
    response.write(data)

    return response
