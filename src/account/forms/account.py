from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _

from ..templatetags.globalpermissions import has_adduser_group, has_addevent_group, has_sendnews_group

import logging
logger = logging.getLogger("helfertool")


logging_group_map = {
    settings.GROUP_ADDUSER: "adduser",
    settings.GROUP_ADDEVENT: "addevent",
    settings.GROUP_SENDNEWS: "sendnews",
}


def _change_permission(user, groupname, has_perm, admin_user):
    group, created = Group.objects.get_or_create(name=groupname)

    if has_perm:
        user.groups.add(group)

        logger.info("permission granted", extra={
            'user': admin_user,
            'permission': logging_group_map[groupname],
            'changed_user': user,
        })
    else:
        user.groups.remove(group)

        logger.info("permission revoked", extra={
            'user': admin_user,
            'permission': logging_group_map[groupname],
            'changed_user': user,
        })


def _user_flag_changeable(user, flag):
    if user.has_usable_password():
        return True

    if hasattr(settings, "AUTH_LDAP_USER_FLAGS_BY_GROUP"):
        return settings.AUTH_LDAP_USER_FLAGS_BY_GROUP.get(flag, None) is None

    return True


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1",
                  "password2")
        widgets = {
            "username": forms.TextInput(attrs={
                'addon_before': settings.LOCAL_USER_CHAR or '',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        for f in ("email", "first_name", "last_name"):
            self.fields[f].required = True

    def clean(self):
        # add LOCAL_USER_CHAR to the beginning
        char = settings.LOCAL_USER_CHAR
        if char:
            if not self.cleaned_data.get('username').startswith(char):
                self.cleaned_data['username'] = char + \
                    self.cleaned_data.get('username')

        return super(CreateUserForm, self).clean()


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "is_active", "is_superuser")

    def __init__(self, *args, **kwargs):
        self._admin_user = kwargs.pop("admin_user")

        super(EditUserForm, self).__init__(*args, **kwargs)

        # set required fields
        for f in ("first_name", "last_name", "email"):
            self.fields[f].required = True

        # adjust labels of active and superuser flags
        self._active_initial = self.instance.is_active
        if _user_flag_changeable(self.instance, "is_active"):
            self.fields["is_active"].help_text = ""
        else:
            self.fields["is_active"].help_text = _("Managed by LDAP group")
            self.fields["is_active"].disabled = True

        self._superuser_initial = self.instance.is_superuser
        self.fields["is_superuser"].label = _("Administrator")
        if _user_flag_changeable(self.instance, "is_superuser"):
            self.fields["is_superuser"].help_text = ""
        else:
            self.fields["is_superuser"].help_text = _("Managed by LDAP group")
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
        self._sendnews_initial = has_sendnews_group(self.instance)
        self.fields["perm_sendnews"] = forms.BooleanField(
            label=_("Send newsletter"),
            required=False,
            initial=self._sendnews_initial,
        )

    def save(self, commit=True):
        instance = super(EditUserForm, self).save(commit)

        # logging for active flag
        if self.cleaned_data.get("is_active") != self._active_initial:
            if self.cleaned_data.get("is_active"):
                logger.info("user enabled", extra={
                    'user': self._admin_user,
                    'changed_user': self.instance,
                })
            else:
                logger.info("user disabled", extra={
                    'user': self._admin_user,
                    'changed_user': self.instance,
                })

        # logging for superuser flag
        if self.cleaned_data.get("is_superuser") != self._superuser_initial:
            if self.cleaned_data.get("is_superuser"):
                logger.info("administrator added", extra={
                    'user': self._admin_user,
                    'changed_user': self.instance,
                })
            else:
                logger.info("administrator removed", extra={
                    'user': self._admin_user,
                    'changed_user': self.instance,
                })

        # remove all permissions for administrators
        if self.cleaned_data.get("is_superuser"):
            self.cleaned_data["perm_adduser"] = False
            self.cleaned_data["perm_addevent"] = False
            self.cleaned_data["perm_sendnews"] = False

        # change permissions
        if self.cleaned_data.get("perm_adduser") != self._adduser_initial:
            _change_permission(self.instance, settings.GROUP_ADDUSER,
                               self.cleaned_data.get("perm_adduser"),
                               self._admin_user)

        if self.cleaned_data.get("perm_addevent") != self._addevent_initial:
            _change_permission(self.instance, settings.GROUP_ADDEVENT,
                               self.cleaned_data.get("perm_addevent"),
                               self._admin_user)

        if self.cleaned_data.get("perm_sendnews") != self._sendnews_initial:
            _change_permission(self.instance, settings.GROUP_SENDNEWS,
                               self.cleaned_data.get("perm_sendnews"),
                               self._admin_user)

        return instance
