from django import forms

from ..models import BadgeDesign, BadgeSettings, BadgePermission, BadgeRole, \
    BadgeDefaults, Badge, Job


class BadgeSettingsForm(forms.ModelForm):
    class Meta:
        model = BadgeSettings
        exclude = ['event', 'defaults', ]


class BadgeDefaultsForm(forms.ModelForm):
    class Meta:
        model = BadgeDefaults
        fields = ['role', 'design', ]

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings')

        super(BadgeDefaultsForm, self).__init__(*args, **kwargs)

        # restrict roles to this event
        self.fields['role'].queryset = BadgeRole.objects.filter(
            badge_settings=self.settings)
        self.fields['design'].queryset = BadgeDesign.objects.filter(
            badge_settings=self.settings)


class BadgeJobDefaultsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(BadgeJobDefaultsForm, self).__init__(*args, **kwargs)

        # available roles and designs
        roles = BadgeRole.objects.filter(
            badge_settings=self.event.badge_settings)
        designs = BadgeDesign.objects.filter(
            badge_settings=self.event.badge_settings)

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
            badge_settings=self.settings)

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
