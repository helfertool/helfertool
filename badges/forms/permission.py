from django import forms

from ..models import BadgePermission


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
