from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission

from ..forms import CreateUserForm, EditUserForm, DeleteUserForm
from ..templatetags.globalpermissions import has_adduser_group

import logging
logger = logging.getLogger("helfertool.account")


@login_required
@never_cache
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
@never_cache
def view_user(request, user_pk=None):
    if user_pk:
        user = get_object_or_404(get_user_model(), pk=user_pk)
    else:
        user = request.user

    # handle own and other user differently
    is_own_user = request.user == user

    # only superusers can view/change other users
    if not request.user.is_superuser and not is_own_user:
        return nopermission(request)

    # superusers do not need to enter the old password, except for the own account
    if request.user.is_superuser and not is_own_user:
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
        # user from LDAP/OpenID Connect
        pw_form = None

    context = {
        "changed_user": user,
        "is_own_user": is_own_user,
        "pw_form": pw_form
    }
    return render(request, 'account/view_user.html', context)


@login_required
@never_cache
def edit_user(request, user_pk):
    # check permission
    if not request.user.is_superuser:
        return nopermission(request)

    changed_user = get_object_or_404(get_user_model(), pk=user_pk)

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
@never_cache
def delete_user(request, user_pk):
    # check permission
    if not request.user.is_superuser:
        return nopermission(request)

    deleted_user = get_object_or_404(get_user_model(), pk=user_pk)

    form = DeleteUserForm(request.POST or None, instance=deleted_user)

    if form.is_valid():
        logger.info("user deleted", extra={
            'user': request.user,
            'deleted_user': deleted_user.username,
        })

        form.delete()

        return redirect('account:list_users')

    context = {
        'form': form,
        'deleted_user': deleted_user,
    }
    return render(request, 'account/delete_user.html', context)


@login_required
@never_cache
def list_users(request):
    # check permission
    if not request.user.is_superuser:
        return nopermission(request)

    # get users based on search term
    search = request.GET.get("search")
    if search:
        all_users = get_user_model().objects.filter(Q(username__icontains=search)
                                                    | Q(first_name__icontains=search)
                                                    | Q(last_name__icontains=search)
                                                    | Q(email__icontains=search)).order_by('last_name')
    else:
        all_users = get_user_model().objects.all().order_by("last_name")

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
    elif filterstr == "sendnews" and settings.FEATURES_NEWSLETTER:
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
