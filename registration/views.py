from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _

from io import BytesIO

from .models import Event, Job, Helper, Shift, BadgeDesign, Link
from .forms import RegisterForm, EventForm, JobForm, ShiftForm, HelperForm, \
                   HelperDeleteForm, ShiftDeleteForm, JobDeleteForm, \
                   EventDeleteForm, LinkDeleteForm, UsernameForm, DeleteForm, \
                   UserCreationForm, LinkForm, BadgeDesignForm
from .utils import escape_filename
from .export.excel import xlsx
from .export.pdf import pdf
from .templatetags.permissions import has_group, has_addevent_group, \
                                      has_adduser_group, has_perm_group

def nopermission(request):
    return render(request, 'registration/admin/nopermission.html')

def is_involved(user, event_url_name=None, admin_required=False):
    if user.is_superuser:
        return True

    try:
        event = Event.objects.get(url_name=event_url_name)
        if admin_required:
            return event.is_admin(user)
        else:
            return event.is_involved(user)
    except Event.DoesNotExist:
        pass

    return False

def is_admin(user, event_url_name=None):
    return is_involved(user, event_url_name, admin_required=True)

def get_or_404(event_url_name=None, job_pk=None, shift_pk=None,
                   helper_pk=None):

    # default values
    event, job, shift, helper = None, None, None, None

    # get all data, if needed
    if event_url_name:
        event = get_object_or_404(Event, url_name=event_url_name)
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)
    if shift_pk:
        shift = get_object_or_404(Shift, pk=shift_pk)
    if helper_pk:
        helper = get_object_or_404(Helper, pk=helper_pk)

    # sanity checks
    if event and job and job.event != event:
        raise Http404

    if job and shift and shift.job != job:
        raise Http404

    # return data
    return event, job, shift, helper


def index(request):
    events = Event.objects.all()

    # check is user is admin
    for e in events:
        e.involved = e.is_involved(request.user)

    # filter events, that are not active and where user is not admin
    active_events = [e for e in events if e.active]
    involved_events = [e for e in events if not e.active and e.involved]

    context = {'active_events': active_events,
               'involved_events': involved_events}
    return render(request, 'registration/index.html', context)

def form(request, event_url_name, link_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # get link if given
    link = None
    if link_pk:
        try:
            link = Link.objects.get(pk=link_pk)
        except Link.DoesNotExist as e:
            # show some message when link does not exist
            context = {'event': event}
            return render(request, 'registration/invalid_link.html', context)

        # check if link belongs to event
        if link.event != event:
            raise Http404()

    # check permission
    if not event.active and not link:
        # not logged in -> show login form
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # logged in -> check permission
        elif not event.is_involved(request.user):
            return nopermission(request)

    # handle form
    form = RegisterForm(request.POST or None, event=event, link=link)

    if form.is_valid():
        helper = form.save()

        # if mail validation if necessary: helper is not validated
        if event.mail_validation:
            helper.validated = False
            helper.save()

        helper.send_mail(request)
        return HttpResponseRedirect(reverse('registered', args=[event.url_name, helper.pk]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/form.html', context)

def registered(request, event_url_name, helper_id):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_id)

    context = {'event': event,
               'data': helper}
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

@login_required
def admin(request, event_url_name=None):
    # check permission
    if not (is_involved(request.user, event_url_name) or \
            has_perm_group(request.user)):
        return nopermission(request)

    # get event
    event = None
    involved = False
    if event_url_name:
        event = get_object_or_404(Event, url_name=event_url_name)

    # response
    context = {'event': event}
    return render(request, 'registration/admin/index.html', context)


@login_required
def edit_event(request, event_url_name=None):
    # TODO shorten
    # check permission
    if event_url_name:
        # event exists -> superuser or admin
        if not is_admin(request.user, event_url_name):
            return nopermission(request)
    else:
        # event will be created -> superuser or addevent group
        if not (request.user.is_superuser or has_addevent_group(request.user)):
            return nopermission(request)

    # get event
    event = None
    if event_url_name:
        event = get_object_or_404(Event, url_name=event_url_name)

    # handle form
    form = EventForm(request.POST or None, instance=event)

    if form.is_valid():
        event = form.save()

        if not event_url_name:
            messages.success(request, _("Event was created: %(event)s") % {'event': event.name})

        # redirect to this page, so reload does not send the form data again
        # if the event was created, this redirects to the event settings
        return HttpResponseRedirect(reverse('edit_event', args=[form['url_name'].value()]))

    # get event without possible invalid modifications from form
    saved_event = None
    if event_url_name:
        saved_event = get_object_or_404(Event, url_name=event_url_name)

    # render page
    context = {'event': saved_event,
               'form': form}
    return render(request, 'registration/admin/edit_event.html', context)

@login_required
def jobs_and_shifts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # list all jobs and shifts
    context = {'event': event}
    return render(request, 'registration/admin/jobs_and_shifts.html', context)


@login_required
def edit_job(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # get job, if available
    job = None
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

    # form
    form = JobForm(request.POST or None, instance=job, event=event)

    if form.is_valid():
        job = form.save()
        return HttpResponseRedirect(reverse('jobs_and_shifts', args=[event_url_name]))

    # render page
    context = {'event': event,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/edit_job.html', context)

@login_required
def edit_shift(request, event_url_name, job_pk, shift_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, job_pk, shift_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = ShiftForm(request.POST or None, instance=shift, job=job)

    if form.is_valid():
        job = form.save()
        return HttpResponseRedirect(reverse('jobs_and_shifts', args=[event_url_name]))

    # render page
    context = {'event': job.event,
               'job': job,
               'shift': shift,
               'form': form}
    return render(request, 'registration/admin/edit_shift.html', context)

@login_required
def edit_helper(request, event_url_name, helper_pk):
    event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)

    # check permission
    if not helper.can_edit(request.user):
        return nopermission(request)

    # form
    form = HelperForm(request.POST or None, instance=helper)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('helpers', args=[event_url_name]))

    # render page
    context = {'event': event,
               'helper': helper,
               'form': form}
    return render(request, 'registration/admin/edit_helper.html', context)

@login_required
def add_helper(request, event_url_name, shift_pk=None, job_pk=None):
    """ Add helper or coordinator.

    If shift is given, a helper is added. If job is given, a coordinator is added.
    """
    event, job, shift, helper = get_or_404(event_url_name, shift_pk=shift_pk, job_pk=job_pk)

    # TODO: check if shift or job is given

    if not job:
        job = shift.job

    # check permission
    if not job.is_admin(request.user):
        return nopermission(request)

    # form
    if job_pk:
        # add coordinator
        form = HelperForm(request.POST or None, job=job)
    else:
        # add helper
        form = HelperForm(request.POST or None, shift=shift)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('jobhelpers', args=[event_url_name, job.pk]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_helper.html', context)

@login_required
def delete_helper(request, event_url_name, helper_pk, job_pk):
    event, job, shift, helper = get_or_404(event_url_name,
                                               job_pk=job_pk,
                                               helper_pk=helper_pk)
    # check permission
    if not helper.can_edit(request.user):
        return nopermission(request)

    # form
    form = HelperDeleteForm(request.POST or None, instance=helper)

    if form.is_valid():
        # check permission
        allowed = True
        for shift in form.get_deleted_shifts():
            if not shift.job.is_admin(request.user):
                allowed = False
                messages.error(request, _("You cannot delete the helper from "
                                          "other shifts. The helper was not "
                                          "deleted"))
                break

        # delete shifts or complete helpers
        if allowed:
            form.delete()
            messages.success(request, _("Helper deleted: %(name)s") % {'name': helper.full_name})

        # redirect to shift
        return HttpResponseRedirect(reverse('jobhelpers', args=[event_url_name, job.pk]))

    # render page
    context = {'event': event,
               'helper': helper,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/delete_helper.html', context)

@login_required
def delete_shift(request, event_url_name, job_pk, shift_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk, shift_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = ShiftDeleteForm(request.POST or None, instance=shift)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Shift deleted"))

        # redirect to shift
        return HttpResponseRedirect(reverse('jobs_and_shifts', args=[event_url_name]))

    # render page
    context = {'event': event,
               'shift': shift,
               'job': job,
               'form': form}
    return render(request, 'registration/admin/delete_shift.html', context)

@login_required
def delete_job(request, event_url_name, job_pk):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = JobDeleteForm(request.POST or None, instance=job)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Job deleted: %(name)s") % {'name': job.name})


        # redirect to shift
        return HttpResponseRedirect(reverse('jobs_and_shifts', args=[event_url_name]))

    # check, if there are helpers registered
    helpers_registered = False
    for shift in job.shift_set.all():
        if shift.helper_set.count() > 0:
            helpers_registered = True
            break

    # render page
    context = {'event': event,
               'job': job,
               'helpers_registered': helpers_registered,
               'form': form}
    return render(request, 'registration/admin/delete_job.html', context)

@login_required
def delete_event(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # form
    form = EventDeleteForm(request.POST or None, instance=event)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Event deleted: %(name)s") % {'name': event.name})

        # redirect to shift
        return HttpResponseRedirect(reverse('index'))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/delete_event.html', context)

@login_required
def delete_link(request, event_url_name, link_pk):
    event = get_object_or_404(Event, url_name=event_url_name)
    link = get_object_or_404(Link, pk=link_pk)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if event matches
    if event != link.event:
        raise Http404()

    # form
    form = LinkDeleteForm(request.POST or None, instance=link)

    if form.is_valid():
        form.delete()
        messages.success(request, _("Link deleted"))

        # redirect to shift
        return HttpResponseRedirect(reverse('links', args=[event_url_name]))

    # render page
    context = {'event': event,
               'link': link,
               'form': form}
    return render(request, 'registration/admin/delete_link.html', context)

@login_required
def helpers(request, event_url_name, job_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_involved(request.user):
        return nopermission(request)

    # helpers of one job
    if job_pk:
        job = get_object_or_404(Job, pk=job_pk)

        # check permission
        if not job.is_admin(request.user):
            return nopermission(request)

        # show list of helpers
        context = {'event': event, 'job': job}
        return render(request, 'registration/admin/helpers_for_job.html', context)

    # overview over jobs
    context = {'event': event}
    return render(request, 'registration/admin/helpers.html', context)

@login_required
def permissions(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # users, that can add users
    users_adduser = User.objects.filter(groups__name__in=[settings.GROUP_ADDUSER, ])

    # users, that can add users
    users_addevent = User.objects.filter(groups__name__in=[settings.GROUP_ADDEVENT, ])

    # form for adduser
    form_adduser = UsernameForm(request.POST or None, prefix='adduser')
    if form_adduser.is_valid():
        user = form_adduser.get_user()
        if user:
            group, created = Group.objects.get_or_create(name=settings.GROUP_ADDUSER)
            user.groups.add(group)
            messages.success(request, _("%(username)s can add users now") % {'username': user})

    # form for addevent
    form_addevent = UsernameForm(request.POST or None, prefix='addevent')
    if form_addevent.is_valid():
        user = form_addevent.get_user()
        if user:
            group, created = Group.objects.get_or_create(name=settings.GROUP_ADDEVENT)
            user.groups.add(group)
            messages.success(request, _("%(username)s can add events now") % {'username': user})

    context = {'users_adduser': users_adduser,
               'users_addevent': users_addevent,
               'form_adduser': form_adduser,
               'form_addevent': form_addevent}
    return render(request, 'registration/admin/permissions.html', context)

@login_required
def delete_permission(request, user_pk, groupname):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # get user
    user = get_object_or_404(User, pk=user_pk)

    # validate group (is only set in urls, so should be ok)
    if not groupname in (settings.GROUP_ADDUSER, settings.GROUP_ADDEVENT):
        raise Http404()

    # form
    form = DeleteForm(request.POST or None)
    if form.is_valid():
        # delete from group
        group = Group.objects.get(name=groupname)
        if group:
            user.groups.remove(group)

        # notification
        messages.success(request, _("Removed permission for user %(username)s") % {'username': user})

        # redirect to overview over permissions
        return HttpResponseRedirect(reverse('permissions'))

    context = {'form': form,
               'user': user}
    return render(request, 'registration/admin/delete_permission.html', context)

@login_required
def add_user(request):
    # check permission
    if not (request.user.is_superuser or has_adduser_group(request.user)):
        return nopermission(request)

    # form
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        messages.success(request, _("Added user %(username)s" % {'username': user}))
        return HttpResponseRedirect(reverse('add_user'))

    context = {'form': form}
    return render(request, 'registration/admin/add_user.html', context)

@login_required
def export(request, event_url_name, type, job_pk=None):
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

    # escape filename
    filename = escape_filename(filename)

    # create buffer
    buffer = BytesIO()

    # do filetype specific stuff
    if type == 'excel':
        filename = "%s.xlsx" % filename
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        xlsx(buffer, event, jobs)
    elif type == 'pdf':
        filename = "%s.pdf" % filename
        content_type = 'application/pdf'
        pdf(buffer, event, jobs)

    # start http response
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # close buffer, send file
    data = buffer.getvalue()
    buffer.close()
    response.write(data)

    return response

@login_required
def coordinators(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    if not event.is_involved(request.user):
        return nopermission(request)

    context = {'event': event}
    return render(request, 'registration/admin/coordinators.html', context)

@login_required
def links(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # get all links
    links = event.link_set.all()

    context = {'event': event,
               'links': links}
    return render(request, 'registration/admin/links.html', context)

@login_required
def edit_link(request, event_url_name, link_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # get job, if available
    link = None
    if link_pk:
        link = get_object_or_404(Link, pk=link_pk)

        if event != link.event:
            raise Http404()

    # form
    form = LinkForm(request.POST or None, instance=link, event=event, creator=request.user)

    if form.is_valid():
        link = form.save()
        return HttpResponseRedirect(reverse('links', args=[event_url_name]))

    # render page
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_link.html', context)

@login_required
def badges(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    context = {'event': event}
    return render(request, 'registration/admin/badges.html', context)

@login_required
def edit_badgedesign(request, event_url_name, design_pk=None, job_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # get BadgeDesign
    design = None
    if design_pk:
        design = get_object_or_404(BadgeDesign, pk=design_pk)

    # form
    form = BadgeDesignForm(request.POST or None, request.FILES or None, instance=design)

    if form.is_valid():
        new_design = form.save()

        # add to job, if newly created
        if job_pk:
            job.badge_design = new_design
            job.save()
        return HttpResponseRedirect(reverse('badges', args=[event.url_name,]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgedesign.html', context)
