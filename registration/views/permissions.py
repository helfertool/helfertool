from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from .utils import nopermission

from ..forms import UsernameForm, DeleteForm


@login_required
def permissions(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # users, that can add users
    users_adduser = User.objects.filter(
        groups__name__in=[settings.GROUP_ADDUSER, ])

    # users, that can add users
    users_addevent = User.objects.filter(
        groups__name__in=[settings.GROUP_ADDEVENT, ])

    # users, that can send news
    users_sendnews = User.objects.filter(
        groups__name__in=[settings.GROUP_SENDNEWS, ])

    # form for adduser
    form_adduser = UsernameForm(request.POST or None, prefix='adduser')
    if form_adduser.is_valid():
        user = form_adduser.get_user()
        if user:
            group, created = Group.objects.get_or_create(
                name=settings.GROUP_ADDUSER)
            user.groups.add(group)
            messages.success(request, _("%(username)s can add users now") %
                             {'username': user})

    # form for addevent
    form_addevent = UsernameForm(request.POST or None, prefix='addevent')
    if form_addevent.is_valid():
        user = form_addevent.get_user()
        if user:
            group, created = Group.objects.get_or_create(
                name=settings.GROUP_ADDEVENT)
            user.groups.add(group)
            messages.success(request, _("%(username)s can add events now") %
                             {'username': user})

    # form for sendnews
    form_sendnews = UsernameForm(request.POST or None, prefix='sendnews')
    if form_sendnews.is_valid():
        user = form_sendnews.get_user()
        if user:
            group, created = Group.objects.get_or_create(
                name=settings.GROUP_SENDNEWS)
            user.groups.add(group)
            messages.success(request, _("%(username)s can send news now") %
                             {'username': user})

    context = {'users_adduser': users_adduser,
               'users_addevent': users_addevent,
               'users_sendnews': users_sendnews,
               'form_adduser': form_adduser,
               'form_addevent': form_addevent,
               'form_sendnews': form_sendnews}
    return render(request, 'registration/admin/permissions.html', context)


@login_required
def delete_permission(request, user_pk, groupname):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # get user
    user = get_object_or_404(User, pk=user_pk)

    # validate group (is only set in urls, so should be ok)
    if groupname not in (settings.GROUP_ADDUSER, settings.GROUP_ADDEVENT,
                         settings.GROUP_SENDNEWS):
        raise Http404()

    # form
    form = DeleteForm(request.POST or None)
    if form.is_valid():
        # delete from group
        group = Group.objects.get(name=groupname)
        if group:
            user.groups.remove(group)

        # notification
        messages.success(request, _("Removed permission for user %(username)s")
                         % {'username': user})

        # redirect to overview over permissions
        return HttpResponseRedirect(reverse('permissions'))

    context = {'form': form,
               'user': user}
    return render(request, 'registration/admin/delete_permission.html',
                  context)
