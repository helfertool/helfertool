from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _

import logging
logger = logging.getLogger("helfertool")

from io import BytesIO

from .export.excel_helper import xlsx_helpers_in_job
from .export.excelimportexport import xlsx_generate_import_template, xlsx_read_import_template
from .export.pdf import pdf
from .forms import ShiftTemplateUploadForm

from registration.views.utils import nopermission
from registration.models import Event, Job, Shift
from registration.utils import escape_filename
from registration.decorators import archived_not_available


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
        if not job.is_admin(request.user):
            return nopermission(request)

        jobs = [job, ]
        job_for_log = job
        filename = "%s - %s" % (event.name, job.name)
    else:
        # check permission
        if not event.is_admin(request.user):
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
        xlsx_helpers_in_job(buffer, event, jobs, date)
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


@login_required
@archived_not_available
def export_job_template(request, event_url_name, job_pk):
    # get event
    event = get_object_or_404(Event, url_name=event_url_name)
    job = get_object_or_404(Job, pk=job_pk)

    # check permission
    if not job.is_admin(request.user):
        return nopermission(request)

    filename = "{}_{}_shifts.xlsx".format(event.name, job.name)
    filename = escape_filename(filename)

    buffer = BytesIO()
    xlsx_generate_import_template(buffer, event, job)

    # log
    logger.info("export_job_template", extra={
        'user': request.user,
        'event': event,
        'job': job,
        'file': filename,
    })

    # start http response
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # close buffer, send file
    data = buffer.getvalue()
    buffer.close()
    response.write(data)

    return response


def convert_giftset(event, giftset_strs):
    """ Lookup all giftset names and resovle them to objects """
    sets = []
    errors = []
    for giftset in giftset_strs:
        if not giftset:
            continue
        try:
            sets.append(event.giftset_set.get(name=giftset))
        except ObjectDoesNotExist:
            errors.append("Giftset " + giftset + "does not exist")

    return errors, sets


def sync_giftsets(shift, giftsets):
    """ Apply the list of giftsets given in giftsets to the shift """
    to_add = []
    to_remove = list(shift.gifts.all())

    for giftset in giftsets:
        giftset = giftset.strip()
        if giftset not in to_remove:
            to_add.append(giftset)
        else:
            to_remove.remove(giftset)

    if to_add:
        shift.gifts.add(*to_add)
    if to_remove:
        shift.gifts.remove(*to_remove)

    return bool(to_add) or bool(to_remove)


@login_required
@archived_not_available
@transaction.atomic()
def import_job_template(request, event_url_name):
    # get event
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = ShiftTemplateUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        errors, job, existing, new = xlsx_read_import_template(request.FILES['importform'], event)

        # check for erros importing the template
        if errors:
            context = {
                'event': event,
                'form': form,
                'errors': errors,
            }
            return render(request, 'importexport/import_errors.html', context)

        savepoint = transaction.savepoint()
        if not form.cleaned_data['update_existing']:
            existing = []
        else:
            # update existing shifts
            for importshift in existing:
                try:
                    shift = job.shift_set.get(id=importshift['id'])
                    importshift['shift'] = shift

                    for prop in ['begin', 'end', 'number', 'name', 'hidden', 'blocked']:
                        importshift[prop+"_changed"] = getattr(shift, prop) != importshift[prop]
                        importshift[prop+"_old"] = getattr(shift, prop)
                        setattr(shift, prop, importshift[prop])

                    gift_errors, giftsets = convert_giftset(event, importshift['giftsets'])
                    if gift_errors:
                        errors += gift_errors
                        continue
                    shift.save()
                    importshift["giftsets_changed"] = sync_giftsets(shift, giftsets)
                    importshift['giftsets'] = giftsets

                except ObjectDoesNotExist:
                    errors.append("Shift with id {} does not exist".format(importshift['id']))

        # insert newly created ones
        for importshift in new:
            # Check if there is already a shift with the same begin and end times and
            # refuse to import them
            print(importshift)
            if job.shift_set.filter(begin=importshift['begin']).filter(end=importshift['end']).exists():
                errors.append(_('Row %(rowid)d: A Shift beginning at %(begin)s and ending at %(end)s already exists. Are you importing an already imported file?') % {
                    'rowid': importshift['excel_row'],
                    'begin': str(importshift['begin']),
                    'end': str(importshift['end'])
                })


            shift = Shift(job=job, **{
                k: importshift[k]
                for k in ['begin', 'end', 'number', 'name', 'hidden', 'blocked']
            })

            gift_errors, giftsets = convert_giftset(event, importshift['giftsets'])
            if gift_errors:
                errors += gift_errors
                continue
            shift.save()
            sync_giftsets(shift, giftsets)
            importshift['giftsets'] = giftsets

        # Check for shift import errors
        if errors:
            transaction.savepoint_rollback(savepoint)
            context = {
                'event': event,
                'form': form,
                'errors': errors,
            }
            return render(request, 'importexport/import_errors.html', context)

        transaction.savepoint_commit(savepoint)
        # import was successful
        context = {
            'event': event,
            'job': job,
            'existing': existing,
            'new': new,
        }
        return render(request, 'importexport/import_overview.html', context)

    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'importexport/import_form.html', context)
