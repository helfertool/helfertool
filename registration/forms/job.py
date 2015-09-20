from django import forms

from ..models import Job, BadgeRole


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ['name', 'description', 'event', 'coordinators',
                   'badge_design', ]
        widgets = {
            'job_admins': forms.SelectMultiple(attrs={'class': 'duallistbox'}),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(JobForm, self).__init__(*args, **kwargs)

        # remove badge_role field if badge creation is disabled
        if not self.event.badges:
            self.fields.pop('badge_role')

        # restrict badge roles
        self.fields['badge_role'].queryset = BadgeRole.objects.filter(
            badge_settings=self.event.badge_settings)

    def save(self, commit=True):
        instance = super(JobForm, self).save(False)  # event is missing

        # add event
        instance.event = self.event

        if commit:
            instance.save()

        self.save_m2m()  # save m2m, otherwise job_admins is lost

        return instance


class JobDeleteForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = []

    def delete(self):
        self.instance.delete()
