from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import Helper, Shift


class HelperForm(forms.ModelForm):
    class Meta:
        model = Helper
        exclude = ['event', 'shifts', ]

    def __init__(self, *args, **kwargs):
        self.related_event = kwargs.pop('event')

        self.shift = None
        if 'shift' in kwargs:
            self.shift = kwargs.pop('shift')

        self.job = None
        if 'job' in kwargs:
            self.job = kwargs.pop('job')

        super(HelperForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(HelperForm, self).clean()

        if self.shift and self.shift.is_full():
            raise ValidationError(_("The shift is full already."))

    def save(self, commit=True):
        instance = super(HelperForm, self).save(False)

        instance.event = self.related_event

        if commit:
            instance.save()

        if self.shift:
            instance.shifts.add(self.shift)
            self.save_m2m()

        if self.job:
            self.job.coordinators.add(self.instance)

        return instance


class HelperDeleteForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', 'shifts', ]
        widgets = {
            'shifts': forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        self.shift = kwargs.pop('shift')
        self.user = kwargs.pop('user')
        self.show_all_shifts = kwargs.pop('show_all_shifts')

        super(HelperDeleteForm, self).__init__(*args, **kwargs)

        # show only the one specified shift ot shifts, where the helper is
        # registered
        if self.show_all_shifts:
            self.fields['shifts'].queryset = self.instance.shifts
        else:
            self.fields['shifts'].queryset = Shift.objects.filter(
                pk=self.shift.pk)  # we need a queryset, not a Shift object

        # make prename, surname and email readonly
        for name in ('prename', 'surname', 'email'):
            self.fields[name].widget.attrs['readonly'] = True

    def clean(self):
        super(HelperDeleteForm, self).clean()

        # check if user is admin for all shifts that will be deleted
        for shift in self.get_deleted_shifts():
            if not shift.job.is_admin(self.user):
                raise ValidationError(_("You are not allowed to delete a "
                                        "helper from the job \"%(jobname)s\"")
                                      % {'jobname': shift.job.name})

    def get_deleted_shifts(self):
        return self.cleaned_data['shifts']

    def delete(self):
        # delete all selected shifts
        for shift in self.cleaned_data['shifts']:
            self.instance.shifts.remove(shift)


class HelperDeleteCoordinatorForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', ]

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job')

        super(HelperDeleteCoordinatorForm, self).__init__(*args, **kwargs)

        # make prename, surname and email readonly
        for name in ('prename', 'surname', 'email'):
            self.fields[name].widget.attrs['readonly'] = True

    def delete(self):
        self.job.coordinators.remove(self.instance)
