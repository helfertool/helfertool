from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from ..creator import BadgeCreator, BadgeCreatorError
from ..checks import warnings_for_job

from registration.views.utils import nopermission, get_or_404
from registration.models import Event
from registration.utils import escape_filename

from .utils import notactive


@login_required
def index(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # check if all necessary settings are done
    possible = event.badge_settings.creation_possible()

    # number for warnings for each job
    jobs = event.job_set.all()
    for job in jobs:
        job.num_warnings = len(warnings_for_job(job))

    context = {'event': event,
               'jobs': jobs,
               'possible': possible}
    return render(request, 'badges/index.html', context)


@login_required
def warnings(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # TODO: check if possible

    helpers = warnings_for_job(job)

    # render
    context = {'event': event,
               'helpers': helpers}
    return render(request, 'badges/warnings.html', context)


@login_required
def generate(request, event_url_name, job_pk=None, generate_all=False):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # TODO: check if possible, show error page

    # badge creation
    creator = BadgeCreator(event.badge_settings)

    # skip already printed badges?
    skip_printed = event.badge_settings.barcodes and not generate_all

    # jobs that should be handled
    if job:
        jobs = [job, ]
        filename = job.name
    else:
        jobs = event.job_set.all()
        filename = event.name

    # add helpers and coordinators
    for j in jobs:
        for h in j.helpers_and_coordinators():
            # skip if badge was printed already
            # (and this behaviour is requested)
            if skip_printed and h.badge.printed:
                continue

            helpers_job = h.badge.get_job()
            # print badge only if this is the primary job or the job is
            # unambiguous
            if (not helpers_job or helpers_job == j):
                creator.add_helper(h)

    # generate
    try:
        pdf_filename = creator.generate()
    except BadgeCreatorError as e:
        # remove temp files
        creator.finish()

        # return error message
        context = {'event': event,
                   'error': e.value,
                   'latex_output': e.get_latex_output()}
        return render(request, 'badges/failed.html',
                      context)

    # output
    filename = escape_filename("%s.pdf" % filename)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # send file
    with open(pdf_filename, 'rb') as f:
        response.write(f.read())

    # finish badge generation (delete files)
    creator.finish()

    return response
