from django import forms
from django.core.exceptions import ValidationError

from ..models import Helper


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
            raise ValidationError("The shift is full already.")

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
        super(HelperDeleteForm, self).__init__(*args, **kwargs)

        # show only shifts, where the helper is registered
        self.fields['shifts'].queryset = self.instance.shifts

        # make prename, surname and email readonly
        for name in ('prename', 'surname', 'email'):
            self.fields[name].widget.attrs['readonly'] = True

    def get_deleted_shifts(self):
        return self.cleaned_data['shifts']

    def delete(self):
        # delete all selected shifts
        for shift in self.cleaned_data['shifts']:
            self.instance.shifts.remove(shift)
