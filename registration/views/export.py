from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from io import BytesIO

from .utils import nopermission

from ..models import Event, Job, Shift
from ..utils import escape_filename
from ..export.excel import xlsx
from ..export.pdf import pdf
from ..decorators import archived_not_available


@login_required
@archived_not_available
def export(request, event_url_name, type, job_pk=None, date_str=None):
    # check for valid export type
    if type not in ["excel", "pdf"]:
        raise Http404

    # get event
    event = get_object_or_404(Event, url_name=event_url_name)

    # list of jobs for export
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

        # check permission
        if not job.is_admin(request.user):
            return nopermission(request)

        jobs = [job, ]
        filename = "%s - %s" % (event.name, job.name)
    else:
        # check permission
        if not event.is_admin(request.user):
            return nopermission(request)

        jobs = event.job_set.all()
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
            jobs = jobs.filter(shift__begin__date=date)

        filename = "{} - {}_{:02d}_{:02d}".format(filename, date.year,
                                                  date.month, date.day)

    # escape filename
    filename = escape_filename(filename)

    # create buffer
    buffer = BytesIO()

    # do filetype specific stuff
    if type == 'excel':
        filename = "%s.xlsx" % filename
        content_type = "application/vnd.openxmlformats-officedocument" \
                       ".spreadsheetml.sheet"
        xlsx(buffer, event, jobs, date)
    elif type == 'pdf':
        filename = "%s.pdf" % filename
        content_type = 'application/pdf'
        pdf(buffer, event, jobs, date)

    # start http response
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # close buffer, send file
    data = buffer.getvalue()
    buffer.close()
    response.write(data)

    return response
