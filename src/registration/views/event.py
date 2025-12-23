from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from account.templatetags.globalpermissions import has_addevent_group
from helfertool.utils import nopermission, serve_file

from ..decorators import archived_not_available
from ..forms import (
    EventForm,
    EventAdminRolesForm,
    EventAdminRolesAddForm,
    EventDeleteForm,
    EventArchiveForm,
    EventDuplicateForm,
    EventMoveForm,
)
from ..models import Event, EventAdminRoles
from ..permissions import has_access, ACCESS_EVENT_EDIT

import logging

logger = logging.getLogger("helfertool.registration")


@login_required
@never_cache
def edit_event(request, event_url_name=None):
    event = None

    # check permission
    if event_url_name:
        event = get_object_or_404(Event, url_name=event_url_name)
        if not has_access(request.user, event, ACCESS_EVENT_EDIT):
            return nopermission(request)
    else:
        # event will be created -> superuser or addevent group
        if not (request.user.is_superuser or has_addevent_group(request.user)):
            return nopermission(request)

    # handle form
    form = EventForm(request.POST or None, request.FILES or None, instance=event)

    if form.is_valid():
        event = form.save()

        if not event_url_name:
            # event was created at the moment -> add user as admin
            if not request.user.is_superuser:
                event.admins.add(request.user)
            event.save()

            logger.info(
                "event created",
                extra={
                    "user": request.user,
                    "event": event,
                    "source_url": None,
                    "source_pk": None,
                },
            )

            messages.success(request, _("Event was created: %(event)s") % {"event": event.name})
        else:
            logger.info(
                "event changed",
                extra={
                    "user": request.user,
                    "event": event,
                },
            )

        # redirect to this page, so reload does not send the form data again
        # if the event was created, this redirects to the event settings
        return redirect("edit_event", event_url_name=form["url_name"].value())

    # get event without possible invalid modifications from form
    saved_event = None
    if event_url_name:
        saved_event = get_object_or_404(Event, url_name=event_url_name)

    # render page
    context = {"event": saved_event, "form": form}
    return render(request, "registration/admin/edit_event.html", context)


@login_required
@never_cache
def edit_event_admins(request, event_url_name=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT):
        return nopermission(request)

    # one form per existing admin (differentiated by prefix)
    all_forms = []
    event_admin_roles = EventAdminRoles.objects.filter(event=event)
    for event_admin in event_admin_roles:
        form = EventAdminRolesForm(
            request.POST or None, instance=event_admin, prefix="user_{}".format(event_admin.user.pk)
        )
        all_forms.append(form)

    # another form to add one new admin
    add_form = EventAdminRolesAddForm(request.POST or None, prefix="add", event=event)

    # we got a post request -> save
    if request.POST and (all_forms or add_form.is_valid()):
        # remove users without any role from admins (no roles = invalid forms)
        for form in all_forms:
            if form.is_valid():
                if form.has_changed():
                    logger.info(
                        "event adminchanged",
                        extra={
                            "user": request.user,
                            "event": event,
                            "changed_user": form.instance.user.username,
                            "roles": ",".join(form.instance.roles),
                        },
                    )
                    form.save()
            else:
                logger.info(
                    "event adminremoved",
                    extra={
                        "user": request.user,
                        "event": event,
                        "changed_user": form.instance.user.username,
                    },
                )
                form.instance.delete()

        # and save the form for a new admin
        if add_form.is_valid():
            new_admin = add_form.save()

            if new_admin:
                logger.info(
                    "event adminadded",
                    extra={
                        "user": request.user,
                        "event": event,
                        "changed_user": new_admin.user.username,
                        "roles": ",".join(new_admin.roles),
                    },
                )
            return redirect("edit_event_admins", event_url_name=event_url_name)

    context = {"event": event, "forms": all_forms, "add_form": add_form}
    return render(request, "registration/admin/edit_event_admins.html", context)


@login_required
@never_cache
def delete_event(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT):
        return nopermission(request)

    # form
    form = EventDeleteForm(request.POST or None, instance=event)

    if form.is_valid():
        form.delete()

        logger.info(
            "event deleted",
            extra={
                "user": request.user,
                "event": event,
            },
        )

        messages.success(request, _("Event deleted: %(name)s") % {"name": event.name})

        # redirect to shift
        return redirect("index")

    # render page
    context = {"event": event, "form": form}
    return render(request, "registration/admin/delete_event.html", context)


@login_required
@never_cache
@archived_not_available
def archive_event(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT):
        return nopermission(request)

    # form
    form = EventArchiveForm(request.POST or None, instance=event)

    if form.is_valid():
        form.archive()

        logger.info(
            "event archived",
            extra={
                "user": request.user,
                "event": event,
            },
        )

        return redirect("edit_event", event_url_name=event_url_name)

    # render page
    context = {"event": event, "form": form}
    return render(request, "registration/admin/archive_event.html", context)


@login_required
@never_cache
def duplicate_event(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT):
        return nopermission(request)

    # form
    form = EventDuplicateForm(request.POST or None, other_event=event, user=request.user)

    if form.is_valid():
        form.save()

        logger.info(
            "event created",
            extra={
                "user": request.user,
                "event": form.instance,
                "source_url": event.url_name,
                "source_pk": event.pk,
            },
        )

        messages.success(request, _("Event was duplicated: %(event)s") % {"event": form["name"].value()})
        return redirect("edit_event", event_url_name=form["url_name"].value())

    # render page
    context = {"event": event, "form": form}
    return render(request, "registration/admin/duplicate_event.html", context)


@login_required
@never_cache
@archived_not_available
def move_event(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT):
        return nopermission(request)

    # form
    form = EventMoveForm(request.POST or None, instance=event)

    if form.is_valid():
        event = form.save()

        logger.info(
            "event moved",
            extra={
                "user": request.user,
                "event": event,
                "new_date": event.date,
            },
        )

        messages.success(request, _("Event was moved: %(event)s") % {"event": event.name})

        return redirect("edit_event", event_url_name=event_url_name)

    # render page
    context = {"event": event, "form": form}
    return render(request, "registration/admin/move_event.html", context)


@login_required
def get_event_logo(request, event_url_name, logotype):
    if logotype not in ["default", "social"]:
        raise Http404()

    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not has_access(request.user, event, ACCESS_EVENT_EDIT):
        return nopermission(request)

    # output
    if logotype == "default":
        return serve_file(event.logo)
    else:
        return serve_file(event.logo_social)
