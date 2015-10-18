from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404

from .utils import nopermission, get_or_404, is_involved

from ..models import Event, BadgeDesign, BadgePermission, BadgeRole
from ..forms import BadgeSettingsForm, BadgeDesignForm, BadgePermissionForm, \
    BadgeRoleForm, BadgeDefaultsForm, BadgeJobDefaultsForm
from ..badges import BadgeCreator, BadgeCreatorError


def notactive(request):
    return render(request, 'registration/admin/badges_not_active.html')


@login_required
def badges(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # check if all necessary settings are done
    possible = event.badge_settings.creation_possible()

    context = {'event': event,
               'possible': possible}
    return render(request, 'registration/admin/badges.html', context)


@login_required
def generate_badges(request, event_url_name, job_pk):
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

    # add helpers and coordinators
    for h in job.helpers_and_coordinators():
        creator.add_helper(h)

    # generate
    try:
        pdf_filename = creator.generate()
    except BadgeCreatorError as e:
        context = {'event': event,
                   'error': e.value,
                   'latex_output': e.get_latex_output()}
        return render(request, 'registration/admin/badges_failed.html',
                      context)

    # output
    filename = "%s.pdf" % job.name

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # send file
    with open(pdf_filename, 'rb') as f:
        response.write(f.read())

    # finish badge generation (delete files)
    creator.finish()

    return response


@login_required
def configure_badges(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # roles
    roles = event.badge_settings.badgerole_set.all()

    # designs
    designs = event.badge_settings.badgedesign_set.all()

    # forms for defaults
    defaults_form = BadgeDefaultsForm(request.POST or None,
                                      instance=event.badge_settings.defaults,
                                      settings=event.badge_settings,
                                      prefix='event')
    job_defaults_form = BadgeJobDefaultsForm(request.POST or None, event=event,
                                             prefix='jobs')

    if defaults_form.is_valid() and job_defaults_form.is_valid():
        defaults_form.save()
        job_defaults_form.save()

        return HttpResponseRedirect(reverse('configure_badges',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'roles': roles,
               'designs': designs,
               'defaults_form': defaults_form,
               'job_defaults_form': job_defaults_form}
    return render(request, 'registration/admin/configure_badges.html', context)


@login_required
def edit_badgesettings(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # form for settings
    form = BadgeSettingsForm(request.POST or None, request.FILES or None,
                             instance=event.badge_settings)

    # for for permissions
    permissions = event.badge_settings.badgepermission_set.all()

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('configure_badges',
                                            args=[event.url_name, ]))

    # render
    context = {'event': event,
               'form': form,
               'permissions': permissions}
    return render(request, 'registration/admin/edit_badgesettings.html',
                  context)

#
# TODO: join the following three views
#


@login_required
def edit_badgepermission(request, event_url_name, permission_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    permission = None
    if permission_pk:
        permission = get_object_or_404(BadgePermission, pk=permission_pk)

        # check if permission belongs to event
        if permission not in event.badge_settings.badgepermission_set.all():
            return Http404()

    # form
    form = BadgePermissionForm(request.POST or None, instance=permission,
                               settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('badgesettings',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgepermission.html',
                  context)


@login_required
def edit_badgerole(request, event_url_name, role_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    role = None
    if role_pk:
        role = get_object_or_404(BadgeRole, pk=role_pk)

        # check if permission belongs to event
        if role not in event.badge_settings.badgerole_set.all():
            return Http404()

    # form
    form = BadgeRoleForm(request.POST or None, instance=role,
                         settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('configure_badges',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgerole.html',
                  context)


@login_required
def edit_badgedesign(request, event_url_name, design_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    design = None
    if design_pk:
        design = get_object_or_404(BadgeDesign, pk=design_pk)

        # check if permission belongs to event
        if design not in event.badge_settings.badgedesign_set.all():
            return Http404()

    # form
    form = BadgeDesignForm(request.POST or None, request.FILES or None,
                           instance=design, settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('configure_badges',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgedesign.html',
                  context)
