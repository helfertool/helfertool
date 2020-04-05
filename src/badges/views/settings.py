from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from ..forms import BadgeSettingsForm, BadgeDefaultsForm, BadgeJobDefaultsForm

from registration.models import Event
from registration.views.utils import nopermission
from registration.permissions import has_access, ACCESS_BADGES_EDIT

from .utils import notactive


@login_required
def settings(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
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

        return HttpResponseRedirect(reverse('badges:settings',
                                            args=[event.url_name, ]))

    context = {'event': event,
               'roles': roles,
               'designs': designs,
               'defaults_form': defaults_form,
               'job_defaults_form': job_defaults_form}
    return render(request, 'badges/settings.html', context)


@login_required
def settings_advanced(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
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

        return HttpResponseRedirect(reverse('badges:settings_advanced',
                                            args=[event.url_name, ]))

    # render
    context = {'event': event,
               'form': form,
               'permissions': permissions}
    return render(request, 'badges/settings_advanced.html',
                  context)


@login_required
def default_template(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_BADGES_EDIT):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # output
    response = HttpResponse(content_type='application/x-tex')
    response['Content-Disposition'] = 'attachment; filename="template.tex"'

    # send file
    with open(django_settings.BADGE_DEFAULT_TEMPLATE, 'rb') as f:
        response.write(f.read())

    return response
