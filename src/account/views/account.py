from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from registration.views.utils import nopermission

from ..forms import CreateUserForm, EditUserForm
from ..templatetags.globalpermissions import has_adduser_group

import logging
logger = logging.getLogger("helfertool")


@login_required
def add_user(request):
    # check permission
    if not (request.user.is_superuser or has_adduser_group(request.user)):
        return nopermission(request)

    # form
    form = CreateUserForm(request.POST or None)

    if form.is_valid():
        user = form.save()

        messages.success(request, _("Added user %(username)s" %
                         {'username': user}))

        logger.info("user created", extra={
            'user': request.user,
            'added_user': user.username,
        })

        return redirect('account:add_user')

    context = {'form': form}
    return render(request, 'account/add_user.html', context)


@login_required
def view_user(request, user_pk=None):
    if user_pk:
        user = get_object_or_404(User, pk=user_pk)
    else:
        user = request.user

    # only superusers can view/change other users
    if not request.user.is_superuser and request.user != user:
        return nopermission(request)

    # superusers do not need to enter the old password, except for the own account
    if request.user.is_superuser and request.user != user:
        pw_form_class = SetPasswordForm
    else:
        pw_form_class = PasswordChangeForm

    # pw change only if there is already a password set
    if user.has_usable_password():
        pw_form = pw_form_class(data=request.POST or None, user=user)

        if pw_form.is_valid():
            pw_form.save()

            if request.user == user:
                update_session_auth_hash(request, pw_form.user)

            logger.info("password changed", extra={
                'user': request.user,
                'changed_user': user.username,
            })

            messages.success(request, _("Changed password successfully"))

            return redirect('account:view_user', user.pk)
    else:
        # user from LDAP
        pw_form = None

    context = {
        "changed_user": user,
        "pw_form": pw_form
    }
    return render(request, 'account/view_user.html', context)


@login_required
def edit_user(request, user_pk):
    # check permission
    if not request.user.is_superuser:
        return nopermission(request)

    changed_user = get_object_or_404(User, pk=user_pk)

    form = EditUserForm(request.POST or None, instance=changed_user, admin_user=request.user)

    if form.is_valid():
        form.save()

        logger.info("user changed", extra={
            'user': request.user,
            'changed_user': changed_user.username,
        })

        return redirect('account:view_user', changed_user.pk)

    context = {
        'form': form,
        'changed_user': changed_user,
    }
    return render(request, 'account/edit_user.html', context)


@login_required
def list_users(request):
    # check permission
    if not request.user.is_superuser:
        return nopermission(request)

    # get users based on search term
    search = request.GET.get("search")
    if search:
        all_users = User.objects.filter(Q(username__icontains=search) |
                                        Q(first_name__icontains=search) |
                                        Q(last_name__icontains=search) |
                                        Q(email__icontains=search)).order_by('last_name')
    else:
        all_users = User.objects.all().order_by("last_name")

    # apply filters
    filterstr = request.GET.get("filter")
    if filterstr == "disabled":
        all_users = all_users.filter(is_active=False)
    elif filterstr == "admin":
        all_users = all_users.filter(is_superuser=True)
    elif filterstr == "addevent":
        all_users = all_users.filter(groups__name__in=[settings.GROUP_ADDEVENT, ])
    elif filterstr == "adduser":
        all_users = all_users.filter(groups__name__in=[settings.GROUP_ADDUSER, ])
    elif filterstr == "sendnews":
        all_users = all_users.filter(groups__name__in=[settings.GROUP_SENDNEWS, ])
    else:
        filterstr = ""

    # paginate
    paginator = Paginator(all_users, 50)
    page = request.GET.get('page')
    users = paginator.get_page(page)

    context = {
        'users': users,
        'search': search or "",
        'filter': filterstr,
    }
    return render(request, 'account/list_users.html',
                  context)
