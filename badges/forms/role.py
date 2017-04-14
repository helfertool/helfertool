from django import forms

from ..models import BadgeRole, BadgePermission


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
            badge_settings=self.settings.pk)

    def save(self, commit=True):
        instance = super(BadgeRoleForm, self).save(False)

        # set settings
        instance.badge_settings = self.settings

        if commit:
            instance.save()

        self.save_m2m()

        return instance


class BadgeRoleDeleteForm(forms.ModelForm):
    class Meta:
        model = BadgeRole
        fields = []

    def delete(self):
        self.instance.delete()
