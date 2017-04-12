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
from ..export.tex_pdf import pdflatex
from ..decorators import archived_not_available


def export_userlist(request, event_url_name, type, template, file_append, event=None):
    # check for valid export type
    if type not in ["excel", "pdf"]:
        print ("Type missmatch: %s" % type)
        raise Http404

    # get event
    if event is None:
        event = { 'event':get_object_or_404(Event, url_name=event_url_name) }

    # list of jobs for export
    # check permission
    if not event['event'].is_admin(request.user):
        return nopermission(request)

    filename = event['event'].name + "_" + file_append

    # escape filename
    filename = escape_filename(filename)

    # create buffer
    with BytesIO() as responsebuffer:
        filename = "%s.pdf" % filename
        content_type = 'application/pdf'
        pdflatex(template, event, responsebuffer)

        # start http response
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        # close buffer, send file
        response.write(responsebuffer.getvalue())
    return response

def calc_shift_property(event):
    missing_shifts = {};
    shift_gifts = {}
    for job in event.job_set.all():
        for shift in job.shift_set.all():
            missing_shifts[shift.id] = shift.number - len(shift.helper_set.all())
            for giftset in shift.gifts.all():
                tmp = {1:0,2:0,3:0,4:0,}
                for gift in giftset.includedgift_set.all():
                    tmp[gift.gift_id] = gift.count
                shift_gifts[shift.id] = {
                        'beer': tmp[1],
                        'food': tmp[2],
                        'vhshirt': tmp[3]/10,
                        'beershirt': tmp[4]/10 }

    return shift_gifts, missing_shifts

def calc_user_gifts(event):
    user_gifts = {}
    for job in event.job_set.all():
        for shift in job.shift_set.all():
            shift_gifts = {}
            for giftset in shift.gifts.all():
                tmp = {1:0,2:0,3:0,4:0,}
                for gift in giftset.includedgift_set.all():
                    tmp[gift.gift_id] = gift.count
                shift_gifts = {
                        'beer': tmp[1],
                        'food': tmp[2],
                        'vhshirt': tmp[3]/10,
                        'beershirt': tmp[4]/10 }

            for helper in shift.helper_set.all():
                print(dir(helper))
                if not helper.id in user_gifts:
                    user_gifts[helper.id] = {
                        'beer': 0,
                        'food': 0,
                        'vhshirt': 0,
                        'beershirt': 0 }
                user_gifts[helper.id]['beer'] += shift_gifts['beer']
                user_gifts[helper.id]['food'] += shift_gifts['food']
                user_gifts[helper.id]['vhshirt'] += shift_gifts['vhshirt']
                user_gifts[helper.id]['beershirt'] += shift_gifts['beershirt']
    return user_gifts

@login_required
@archived_not_available
def export_helpers(request, event_url_name, type):
    return export_userlist(request, event_url_name, type,
                           "registration/tex/full_helper_list.tex", "helfer")


@login_required
@archived_not_available
def export_entry(request, event_url_name, type):
    return export_userlist(request, event_url_name, type,
                           "registration/tex/entry_list.tex", "eintritt")

@login_required
@archived_not_available
def export_giftlist(request, event_url_name, type):

    if type not in ["pdf"]:
        print ("Type missmatch: %s" % type)
        raise Http404

    # get event
    event = get_object_or_404(Event, url_name=event_url_name)

    # list of jobs for export
    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    #Todo: Calculate gifts
    shift_gifts, missing_shifts = calc_shift_property(event)
    e = {
            'event':event,
            'missing_shifts':missing_shifts,
            'shift_gifts': shift_gifts,
    }

    return export_userlist(request, event_url_name, type,
                           "registration/tex/gift_list.tex", "marken", e)

@login_required
@archived_not_available
def export_shirtlist(request, event_url_name, type):

    if type not in ["pdf"]:
        print ("Type missmatch: %s" % type)
        raise Http404

    # get event
    event = get_object_or_404(Event, url_name=event_url_name)

    # list of jobs for export
    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    user_gifts = calc_user_gifts(event)
    e = {
            'event':event,
            'user_gifts': user_gifts,
    }

    return export_userlist(request, event_url_name, type,
                           "registration/tex/helper_shirt_list.tex", "vielhelfer", e)


@login_required
@archived_not_available
def export_beershirtlist(request, event_url_name, type):

    if type not in ["pdf"]:
        print ("Type missmatch: %s" % type)
        raise Http404

    # get event
    event = get_object_or_404(Event, url_name=event_url_name)

    # list of jobs for export
    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    user_gifts = calc_user_gifts(event)
    e = {
            'event':event,
            'helper_gifts': user_gifts,
    }

    return export_userlist(request, event_url_name, type,
                           "registration/tex/beer_shirt_list.tex", "biershirts", e)


