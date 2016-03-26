from django import forms
from django.utils.translation import ugettext as _

from ..models import BadgeDesign, BadgeRole, BadgeDefaults


class BadgeDefaultsForm(forms.ModelForm):
    class Meta:
        model = BadgeDefaults
        fields = ['role', 'design', ]

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings')

        super(BadgeDefaultsForm, self).__init__(*args, **kwargs)

        # restrict roles to this event
        self.fields['role'].queryset = BadgeRole.objects.filter(
            badge_settings=self.settings.pk)
        self.fields['design'].queryset = BadgeDesign.objects.filter(
            badge_settings=self.settings.pk)


class BadgeJobDefaultsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(BadgeJobDefaultsForm, self).__init__(*args, **kwargs)

        # available roles and designs
        roles = BadgeRole.objects.filter(
            badge_settings=self.event.badge_settings.pk)
        designs = BadgeDesign.objects.filter(
            badge_settings=self.event.badge_settings.pk)

        # add fields for each job
        for job in self.event.job_set.all():
            self.fields['job_%d_design' % job.pk] = forms.ModelChoiceField(
                queryset=designs, required=False,
                initial=job.badge_defaults.design)
            self.fields['job_%d_role' % job.pk] = forms.ModelChoiceField(
                queryset=roles, required=False,
                initial=job.badge_defaults.role)
            self.fields['job_%d_no_def_role' % job.pk] = forms.BooleanField(
                initial=job.badge_defaults.no_default_role,
                required=False,
                label=_("No default role"))

    def save(self):
        for job in self.event.job_set.all():
            job.badge_defaults.design = self.cleaned_data[
                'job_%d_design' % job.pk]
            job.badge_defaults.role = self.cleaned_data['job_%d_role' % job.pk]
            job.badge_defaults.no_default_role = \
                self.cleaned_data['job_%d_no_def_role' % job.pk]
            job.badge_defaults.save()
