from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from django_select2.forms import Select2Widget

from helfertool.forms.widgets import user_label_from_instance
from registration.models import EventAdminRoles, JobAdminRoles, Link
from mail.models import SentMail
from inventory.models import Inventory
from toollog.models import LogEntry

from ..templatetags.globalpermissions import has_adduser_group, has_addevent_group, has_sendnews_group

import logging

logger = logging.getLogger("helfertool.account")


logging_group_map = {
    settings.GROUP_ADDUSER: "adduser",
    settings.GROUP_ADDEVENT: "addevent",
    settings.GROUP_SENDNEWS: "sendnews",
}


def _change_permission(user, groupname, has_perm, admin_user):
    group, created = Group.objects.get_or_create(name=groupname)

    if has_perm:
        user.groups.add(group)

        logger.info(
            "permission granted",
            extra={
                "user": admin_user,
                "permission": logging_group_map[groupname],
                "changed_user": user,
            },
        )
    else:
        user.groups.remove(group)

        logger.info(
            "permission revoked",
            extra={
                "user": admin_user,
                "permission": logging_group_map[groupname],
                "changed_user": user,
            },
        )


def _user_flag_changeable(user, flag):
    # local account -> yes
    if user.has_usable_password():
        return True

    # LDAP enabled -> check the settings
    if (
        hasattr(settings, "AUTH_LDAP_USER_FLAGS_BY_GROUP")
        and settings.AUTH_LDAP_USER_FLAGS_BY_GROUP.get(flag, None) is not None
    ):
        return False

    # OpenID connect enabled -> check the settings
    if settings.OIDC_CUSTOM_PROVIDER_NAME is not None:
        if flag == "is_active" and settings.OIDC_CUSTOM_CLAIM_LOGIN is not None:
            return False
        if flag == "is_superuser" and settings.OIDC_CUSTOM_CLAIM_ADMIN is not None:
            return False

    return True


class CreateUserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "addon_before": settings.LOCAL_USER_CHAR or "",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        for f in ("email", "first_name", "last_name"):
            self.fields[f].required = True

    def clean(self):
        # add LOCAL_USER_CHAR to the beginning
        char = settings.LOCAL_USER_CHAR
        if char and not self.cleaned_data.get("username").startswith(char):
            self.cleaned_data["username"] = char + self.cleaned_data.get("username")

        return super(CreateUserForm, self).clean()


class EditUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email", "is_active", "is_superuser")

    def __init__(self, *args, **kwargs):
        self._admin_user = kwargs.pop("admin_user")

        super(EditUserForm, self).__init__(*args, **kwargs)

        # set attributes for name/email fields
        # if user is local, the fields are required
        # if users is from external idp, the fields cannot be changed
        for f in ("first_name", "last_name", "email"):
            if self.instance.has_usable_password():
                self.fields[f].required = True
            else:
                self.fields[f].help_text = _("Managed by external identity provider")
                self.fields[f].disabled = True

        # adjust labels of active and superuser flags
        self._active_initial = self.instance.is_active
        if _user_flag_changeable(self.instance, "is_active"):
            self.fields["is_active"].help_text = ""
        else:
            self.fields["is_active"].help_text = _("Managed by external identity provider")
            self.fields["is_active"].disabled = True

        self._superuser_initial = self.instance.is_superuser
        self.fields["is_superuser"].label = _("Administrator")
        if _user_flag_changeable(self.instance, "is_superuser"):
            self.fields["is_superuser"].help_text = ""
        else:
            self.fields["is_superuser"].help_text = _("Managed by external identity provider")
            self.fields["is_superuser"].disabled = True

        # permission: adduser
        self._adduser_initial = has_adduser_group(self.instance)
        self.fields["perm_adduser"] = forms.BooleanField(
            label=_("Add users"),
            required=False,
            initial=self._adduser_initial,
        )

        # permission: addevent
        self._addevent_initial = has_addevent_group(self.instance)
        self.fields["perm_addevent"] = forms.BooleanField(
            label=_("Add events"),
            required=False,
            initial=self._addevent_initial,
        )

        # permission: sendnews
        if settings.FEATURES_NEWSLETTER:
            self._sendnews_initial = has_sendnews_group(self.instance)
            self.fields["perm_sendnews"] = forms.BooleanField(
                label=_("Send newsletter"),
                required=False,
                initial=self._sendnews_initial,
            )

    def save(self, commit=True):
        # set is_staff to same value as is_superuser
        self.instance.is_staff = self.cleaned_data.get("is_superuser")

        # save
        instance = super(EditUserForm, self).save(commit)

        # logging for active flag
        if self.cleaned_data.get("is_active") != self._active_initial:
            if self.cleaned_data.get("is_active"):
                logger.info(
                    "user enabled",
                    extra={
                        "user": self._admin_user,
                        "changed_user": self.instance,
                    },
                )
            else:
                logger.info(
                    "user disabled",
                    extra={
                        "user": self._admin_user,
                        "changed_user": self.instance,
                    },
                )

        # logging for superuser flag
        if self.cleaned_data.get("is_superuser") != self._superuser_initial:
            if self.cleaned_data.get("is_superuser"):
                logger.info(
                    "administrator added",
                    extra={
                        "user": self._admin_user,
                        "changed_user": self.instance,
                    },
                )
            else:
                logger.info(
                    "administrator removed",
                    extra={
                        "user": self._admin_user,
                        "changed_user": self.instance,
                    },
                )

        # remove all permissions for administrators
        if self.cleaned_data.get("is_superuser"):
            self.cleaned_data["perm_adduser"] = False
            self.cleaned_data["perm_addevent"] = False
            if settings.FEATURES_NEWSLETTER:
                self.cleaned_data["perm_sendnews"] = False

        # change permissions
        if self.cleaned_data.get("perm_adduser") != self._adduser_initial:
            _change_permission(
                self.instance, settings.GROUP_ADDUSER, self.cleaned_data.get("perm_adduser"), self._admin_user
            )

        if self.cleaned_data.get("perm_addevent") != self._addevent_initial:
            _change_permission(
                self.instance, settings.GROUP_ADDEVENT, self.cleaned_data.get("perm_addevent"), self._admin_user
            )

        if settings.FEATURES_NEWSLETTER and self.cleaned_data.get("perm_sendnews") != self._sendnews_initial:
            _change_permission(
                self.instance, settings.GROUP_SENDNEWS, self.cleaned_data.get("perm_sendnews"), self._admin_user
            )

        return instance


class DeleteUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = []

    def delete(self):
        self.instance.delete()


class MergeUserForm(forms.Form):
    deleted_user = forms.ChoiceField(
        label=_("Other user, which will be deleted"),
        widget=Select2Widget,
    )

    def __init__(self, *args, **kwargs):
        self._remaining_user = kwargs.pop("remaining_user")

        super(MergeUserForm, self).__init__(*args, **kwargs)

        # fill choices for deleted user
        choices = [
            ["", "---"],
        ]
        for u in get_user_model().objects.all():
            if u != self._remaining_user:
                choices.append([u.username, user_label_from_instance(u)])
        self.fields["deleted_user"].choices = choices

    def clean(self):
        cleaned_data = super().clean()

        User = get_user_model()
        try:
            self.deleted_user_obj = User.objects.get(username=cleaned_data["deleted_user"])
        except User.DoesNotExist:
            self.add_error("deleted_user", _("User does not exist"))

    def merge(self):
        # global permissions
        if self.deleted_user_obj.is_superuser:
            self._remaining_user.is_superuser = True
            self._remaining_user.save()

        for groupname in [settings.GROUP_ADDUSER, settings.GROUP_ADDEVENT, settings.GROUP_SENDNEWS]:
            if self.deleted_user_obj.groups.filter(name=groupname).exists():
                group, created = Group.objects.get_or_create(name=groupname)
                self._remaining_user.groups.add(group)

        # registration -> EventAdminRoles
        for admin in EventAdminRoles.objects.filter(user=self.deleted_user_obj):
            try:
                admin_other = EventAdminRoles.objects.get(event=admin.event, user=self._remaining_user)

                # the other user also has admin access -> merge permissions
                # old roles will be deleted together with user later
                self._merge_admin_roles(admin, admin_other)

            except EventAdminRoles.DoesNotExist:
                # the other user does not have admin permissions for the event -> just rewrite existing entry
                admin.user = self._remaining_user
                admin.save()

        # registration -> JobAdminRoles
        for admin in JobAdminRoles.objects.filter(user=self.deleted_user_obj):
            try:
                admin_other = JobAdminRoles.objects.get(job=admin.job, user=self._remaining_user)

                # the other user also has admin access -> merge permissions
                # old roles will be deleted together with user later
                self._merge_admin_roles(admin, admin_other)
            except JobAdminRoles.DoesNotExist:
                # the other user does not have admin permissions for the event -> just rewrite existing entry
                admin.user = self._remaining_user
                admin.save()

        # registration -> Link
        Link.objects.filter(creator=self.deleted_user_obj).update(creator=self._remaining_user)

        # mail -> SentMail
        SentMail.objects.filter(user=self.deleted_user_obj).update(user=self._remaining_user)

        # inventory -> Inventory
        for inventory in Inventory.objects.filter(admins=self.deleted_user_obj):
            if not inventory.admins.filter(pk=self._remaining_user.pk).exists():
                inventory.admins.add(self._remaining_user)
                inventory.save()

        # toollog -> LogEntry
        LogEntry.objects.filter(user=self.deleted_user_obj).update(user=self._remaining_user)

        # get rid of old user
        self.deleted_user_obj.delete()

    def _merge_admin_roles(self, adminroles_deleted, adminroles_remaining):
        for role in adminroles_deleted.roles:
            if role not in adminroles_remaining.roles:
                adminroles_remaining.roles.append(role)
        adminroles_remaining.save()
