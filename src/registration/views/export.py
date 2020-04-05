from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

import logging
logger = logging.getLogger("helfertool")

from io import BytesIO

from .utils import nopermission

from ..models import Event, Job, Shift
from ..utils import escape_filename
from ..export.excel import xlsx
from ..export.pdf import pdf
from ..decorators import archived_not_available
from ..permissions import has_access, ACCESS_EVENT_EXPORT_HELPERS


@login_required
@archived_not_available
def export(request, event_url_name, filetype, job_pk=None, date_str=None):
    # check for valid export type
    if filetype not in ["excel", "pdf"]:
        raise Http404

    # get event
    event = get_object_or_404(Event, url_name=event_url_name)

    # list of jobs for export
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

        # check permission
        if not has_access(request.user, job, ACCESS_EVENT_EXPORT_HELPERS):
            return nopermission(request)

        jobs = [job, ]
        job_for_log = job
        filename = "%s - %s" % (event.name, job.name)
    else:
        # check permission
        if not has_access(request.user, event, ACCESS_EVENT_EXPORT_HELPERS):
            return nopermission(request)

        jobs = event.job_set.all()
        job_for_log = None
        filename = event.name

    # parse date
    date = None
    if date_str:
        try:
            date = parse_date(date_str)
        except ValueError:
            raise Http404

        # check if there are any shifts with this start date
        if not Shift.objects.filter(job__in=jobs, begin__date=date).exists():
            raise Http404

        # if all jobs are shown, exclude all jobs without shifts on this day
        if not job_pk:
            jobs = jobs.filter(shift__begin__date=date).distinct()

        filename = "{} - {}_{:02d}_{:02d}".format(filename, date.year,
                                                  date.month, date.day)

    # escape filename
    filename = escape_filename(filename)

    # create buffer
    buffer = BytesIO()

    # do filetype specific stuff
    if filetype == 'excel':
        filename = "%s.xlsx" % filename
        content_type = "application/vnd.openxmlformats-officedocument" \
                       ".spreadsheetml.sheet"
        xlsx(buffer, event, jobs, date)
    elif filetype == 'pdf':
        filename = "%s.pdf" % filename
        content_type = 'application/pdf'
        pdf(buffer, event, jobs, date)

    # log
    logger.info("export", extra={
        'user': request.user,
        'event': event,
        'job': job_for_log,
        'type': filetype,
        'file': filename,
        'date': date_str,
    })

    # start http response
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # close buffer, send file
    data = buffer.getvalue()
    buffer.close()
    response.write(data)

    return response
