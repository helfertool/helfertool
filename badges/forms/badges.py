from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import magic

from ..models import BadgeDesign, BadgeSettings, BadgePermission, BadgeRole, \
    BadgeDefaults, Badge

from registration.models import Job
from registration.utils import is_image


class BadgeSettingsForm(forms.ModelForm):
    class Meta:
        model = BadgeSettings
        exclude = ['event', 'defaults', ]

    def clean_latex_template(self):
        file = self.cleaned_data['latex_template']

        # check mimetype with libmagic
        filemime = magic.from_buffer(file.read(), mime=True)
        if filemime != b'text/x-tex':
            raise ValidationError(_("File does not contain LaTeX code."))

        # seek to begin (may be necessary for further use?)
        file.seek(0)

        return file


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

    def save(self):
        for job in self.event.job_set.all():
            job.badge_defaults.design = self.cleaned_data[
                'job_%d_design' % job.pk]
            job.badge_defaults.role = self.cleaned_data['job_%d_role' % job.pk]
            job.badge_defaults.save()

#
# join following three forms?
#


class BadgeDesignForm(forms.ModelForm):
    class Meta:
        model = BadgeDesign
        exclude = ['badge_settings', 'name', ]

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings')

        super(BadgeDesignForm, self).__init__(*args, **kwargs)

    def clean_bg_front(self):
        file = self.cleaned_data['bg_front']
        if not is_image(file):
            raise ValidationError(_("The file is not an image."))
        return file

    def clean_bg_back(self):
        file = self.cleaned_data['bg_back']
        if not is_image(file):
            raise ValidationError(_("The file is not an image."))
        return file

    def save(self, commit=True):
        instance = super(BadgeDesignForm, self).save(False)

        # set settings
        instance.badge_settings = self.settings

        if commit:
            instance.save()

        return instance


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
            badge_settings=self.settings.pk)

    def save(self, commit=True):
        instance = super(BadgeRoleForm, self).save(False)

        # set settings
        instance.badge_settings = self.settings

        if commit:
            instance.save()

        self.save_m2m()

        return instance


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        exclude = ['helper', ]

    def __init__(self, *args, **kwargs):
        super(BadgeForm, self).__init__(*args, **kwargs)

        # restrict queryset of primary_job
        jobs = Job.objects.filter(shift__helper=self.instance.helper).\
            distinct()
        coordinated_jobs = self.instance.helper.coordinated_jobs.distinct()

        self.fields['primary_job'].queryset = jobs | coordinated_jobs

        # restrict queryset of custom_role and custom_design
        badge_settings = self.instance.helper.event.badgesettings

        roles = BadgeRole.objects.filter(badge_settings=badge_settings)
        self.fields['custom_role'].queryset = roles

        designs = BadgeDesign.objects.filter(badge_settings=badge_settings)
        self.fields['custom_design'].queryset = designs

    def clean_photo(self):
        file = self.cleaned_data['photo']
        if not is_image(file):
            raise ValidationError(_("The file is not an image."))
        return file


class RegisterBadgeForm(forms.Form):
    badge_id = forms.IntegerField(label='Barcode', widget=forms.TextInput(attrs={'autofocus': ''}))

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        self.badge = None

        super(RegisterBadgeForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(RegisterBadgeForm, self).__init__()

        id = self.cleaned_data.get('badge_id')

        # check if id is given
        if not id:
            raise ValidationError(_("Invalid barcode."))

        # check if badge exists
        try:
            self.badge = Badge.objects.get(pk=id)
        except Badge.DoesNotExist:
            raise ValidationError(_("This badge does not exist. "
                                    "Maybe it was deleted since printing."))

        # check if badge belongs to event
        if self.badge.helper.event != self.event:
            raise ValidationError(_("This badge does not belong to this "
                                    "event."))
