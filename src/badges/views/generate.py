from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from celery.result import AsyncResult

from ..checks import warnings_for_job
from .. import tasks

from registration.decorators import archived_not_available
from registration.views.utils import nopermission, get_or_404
from registration.models import Event
from registration.utils import escape_filename
from registration.permissions import has_access, ACCESS_BADGES_GENERATE

from .utils import notactive


def create_task_dict(task_id, name, event):
    tmp = {}
    tmp['id'] = task_id
    tmp['name'] = name
    tmp['event'] = event.pk

    return tmp


class BadgeTaskResult:
    def __init__(self, task_id, name=None):
        result = AsyncResult(task_id)

        self.id = task_id
        self.name = name

        self.finished = result.successful()
        self.error = result.failed() or result.state == "CREATOR_ERROR"
        self.expired = False
        self.pdf = None
        self.dl_filename = None

        if result.successful():
            pdf, dl_filename, clean_task_id = result.result

            clean_result = AsyncResult(clean_task_id)
            if clean_result.state == 'SUCCESS':
                self.expired = True

            self.pdf = pdf
            self.dl_filename = dl_filename


@login_required
@archived_not_available
def index(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_GENERATE):
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


def tasklist(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # do not return data if user is not authenticated
    if not request.user.is_authenticated:
        context = {'event': event,
                   'tasks': None,
                   'no_login': True}
        return render(request, 'badges/tasklist.html', context)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_GENERATE):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # recently started tasks
    if 'badge_tasks' not in request.session:
        request.session['badge_tasks'] = []

    task_results = []
    task_list_del = []
    for task in request.session['badge_tasks']:
        tmp = BadgeTaskResult(task['id'], task['name'])

        # filter expired tasks
        if tmp.expired:
            task_list_del.append(task)
        elif task['event'] == event.pk:
            task_results.append(tmp)

    # remove expired filtered tasks
    for task in task_list_del:
        request.session['badge_tasks'].remove(task)
    request.session.modified = True

    context = {'event': event,
               'tasks': task_results,
               'no_login': False}
    return render(request, 'badges/tasklist.html', context)


@login_required
@archived_not_available
def warnings(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_GENERATE):
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
@archived_not_available
def generate(request, event_url_name, job_pk=None, generate_all=False):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_GENERATE):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # TODO: check if possible, show error page

    # skip already printed badges?
    skip_printed = event.badge_settings.barcodes and not generate_all

    # start generation
    result = tasks.generate_badges.delay(event.pk, job_pk, skip_printed)

    # name
    name = None
    if job:
        if skip_printed:
            name = _("{} (only unregistered)").format(job.name)
        else:
            name = _("{} (all)").format(job.name)
    else:
        if skip_printed:
            name = _("All unregistered badges")
        else:
            name = _("Really all badges")

    # add to session
    if 'badge_tasks' not in request.session:
        request.session['badge_tasks'] = []

    task = create_task_dict(result.task_id, name, event)

    request.session['badge_tasks'].insert(0, task)
    request.session.modified = True

    return HttpResponseRedirect(reverse('badges:index', args=[event.url_name]))


@login_required
@archived_not_available
def failed(request, event_url_name, task_id):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_GENERATE):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get result
    result = AsyncResult(task_id)

    error = None
    latex_output = None

    if result.failed():
        error = _("Internal Server Error. The admins were notified.")
        mail_admins("Badge generation error", str(result.result),
                    fail_silently=True)
    elif result.state == "CREATOR_ERROR":
        error = result.info['error']
        latex_output = result.info['latex_output']

    # return error message
    context = {'event': event,
               'error': error,
               'latex_output': latex_output}
    return render(request, 'badges/failed.html',
                  context)


@login_required
@archived_not_available
def download(request, event_url_name, task_id):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_GENERATE):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # remove from list
    if 'badge_tasks' not in request.session:
        request.session['badge_tasks'] = []

    del_task = None
    for task in request.session['badge_tasks']:
        if task['id'] == task_id:
            del_task = task
            break

    if del_task:
        request.session['badge_tasks'].remove(del_task)
        request.session.modified = True
    # TODO: files can be deleted also, happens through celery at the moment

    # get result
    badge_task = BadgeTaskResult(task_id)

    if badge_task.finished and not badge_task.expired:
        # output
        filename = escape_filename("%s.pdf" % badge_task.dl_filename)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % \
            filename

        # send file
        with open(badge_task.pdf, 'rb') as f:
            response.write(f.read())

        return response
    else:
        # return error message
        context = {'event': event}
        return render(request, 'badges/download.html',
                      context)
