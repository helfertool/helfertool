from django import forms

from ..models import BadgeDesign, BadgeSettings, BadgePermission, BadgeRole


class BadgeSettingsForm(forms.ModelForm):
    class Meta:
        model = BadgeSettings
        exclude = ['event', 'design', 'permissions', 'role',
                   'coordinator_role', ]

class BadgeDefaultRolesForm(forms.ModelForm):
    class Meta:
        model = BadgeSettings
        fields = ['role', 'coordinator_role', ]

    def __init__(self, *args, **kwargs):
        super(BadgeDefaultRolesForm, self).__init__(*args, **kwargs)

        # restrict roles to this event
        roles = BadgeRole.objects.filter(badge_settings=self.instance)
        self.fields['role'].queryset = roles
        self.fields['coordinator_role'].queryset = roles


class BadgeDesignForm(forms.ModelForm):
    class Meta:
        model = BadgeDesign
        exclude = []


class BadgePermissionForm(forms.ModelForm):
    class Meta:
        model = BadgePermission
        exclude = ['badge_settings', 'name', ]

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings')

        super(BadgePermissionForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(BadgePermissionForm, self).save(False)

        # set settings
        instance.badge_settings = self.settings

        if commit:
            instance.save()

        return instance


class BadgeRoleForm(forms.ModelForm):
    class Meta:
        model = BadgeRole
        exclude = ['badge_settings', 'name', ]
        widgets = {
            'permissions': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings')

        super(BadgeRoleForm, self).__init__(*args, **kwargs)

        # restrict permissions to this event
        self.fields['permissions'].queryset = BadgePermission.objects.filter(
            badge_settings=self.settings)

    def save(self, commit=True):
        instance = super(BadgeRoleForm, self).save(False)

        # set settings
        instance.badge_settings = self.settings

        if commit:
            instance.save()

        self.save_m2m()

        return instance
