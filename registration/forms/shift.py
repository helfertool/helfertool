from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from gifts.models import GiftSet

from ..models import Shift

from .fields import DualListField


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        exclude = ['job', 'archived_number', ]
        field_classes = {
            'gifts': DualListField,
        }
        widgets = {
            'number': forms.NumberInput(attrs={'min': 0}),
            'begin': forms.DateTimeInput(attrs={'class': 'datetime'}),
            'end': forms.DateTimeInput(attrs={'class': 'datetime'}),
        }

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job')

        super(ShiftForm, self).__init__(*args, **kwargs)

        if not self.job.event.gifts:
            self.fields.pop('gifts')
        else:
            self.fields['gifts'].queryset = GiftSet.objects.filter(
                event=self.job.event)

    def clean(self):
        super(ShiftForm, self).clean()

        # this should not be necessary, however it is
        if 'begin' not in self.cleaned_data:
            raise ValidationError(_("The begin of the shift must be set."))
        if 'end' not in self.cleaned_data:
            raise ValidationError(_("The end of the shift must be set."))

        # check times
        if self.cleaned_data.get('begin') > self.cleaned_data.get('end'):
            raise ValidationError(_("The begin of the shift must be before "
                                    "the end."))

    def save(self, commit=True):
        instance = super(ShiftForm, self).save(False)  # event is missing

        # add event
        instance.job = self.job

        if commit:
            instance.save()

        self.save_m2m()  # save m2m, otherwise gifts is lost

        return instance


class ShiftDeleteForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = []

    def delete(self):
        self.instance.delete()
