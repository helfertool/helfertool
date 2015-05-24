from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import defaultfilters as filters
from io import BytesIO
import xlsxwriter

from .models import Event, Job, Helper
from .forms import RegisterForm
from .utils import escape_filename

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

@login_required
def excel(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        context = {'event': event}
        return render(request, 'registration/nopermission.html', context)

    # list of jobs for export
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)
        #jobs = Job.objects.filter(pk=job_pk)
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

    # create xlsx
    workbook = xlsxwriter.Workbook(buffer)

    # export jobs
    for job in jobs:
        worksheet = workbook.add_worksheet(job.name)
        bold = workbook.add_format({'bold': True})

        # header
        worksheet.write(0, 0, "Vorname", bold)
        worksheet.write(0, 1, "Nachname", bold)
        worksheet.write(0, 2, "E-Mail", bold)
        worksheet.write(0, 3, "Handy", bold)
        worksheet.write(0, 4, "T-Shirt", bold)
        worksheet.write(0, 5, "Vegetarier", bold)
        worksheet.write(0, 6, "Kommentar", bold)

        worksheet.freeze_panes(1, 0)
        worksheet.set_column(0, 3, 30)
        worksheet.set_column(4, 5, 10)
        worksheet.set_column(6, 6, 30)

        # the current row
        row=1

        # show all shifts
        for shift in job.shift_set.order_by('begin'):
            worksheet.merge_range(row, 0, row, 6, shift.time(), bold)
            row += 1
            for helper in shift.helper_set.all():
                worksheet.write(row, 0, helper.prename)
                worksheet.write(row, 1, helper.surname)
                worksheet.write(row, 2, helper.email)
                worksheet.write(row, 3, helper.phone)
                worksheet.write(row, 4, helper.get_shirt_display())
                worksheet.write(row, 5, filters.yesno(helper.vegetarian))
                worksheet.write(row, 6, helper.comment)
                row += 1

    # close xlsx
    workbook.close()

    # close buffer, send file
    xlsx = buffer.getvalue()
    buffer.close()
    response.write(xlsx)

    return response
