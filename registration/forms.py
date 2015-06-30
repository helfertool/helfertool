from django import forms
from django.core.exceptions import ValidationError
from django.utils import formats, translation
from django.utils.translation import ugettext as _

from .models import Helper, Shift, Event, Job

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', 'phone', 'shirt', 'vegetarian', 'infection_instruction', 'comment']

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        self.shifts = {}

        super(RegisterForm, self).__init__(*args, **kwargs)

        # remove field for shirt?
        if not event.ask_shirt:
            self.fields.pop('shirt')

        # remove field for vegetarian food?
        if not event.ask_vegetarian:
            self.fields.pop('vegetarian')

        # add fields for shifts
        for job in event.job_set.all():
            for shift in job.shift_set.all():
                id = 'shift_%s' % shift.pk
                self.fields[id] = forms.BooleanField(label=shift,
                                                     required=False)

                # disable button if shift is full
                if shift.is_full():
                    self.fields[id].widget.attrs['disabled'] = True

                # set class if infection instruction is needed for this shift
                if shift.job.infection_instruction:
                    self.fields[id].widget.attrs['class'] = 'infection_instruction'
                    self.fields[id].widget.attrs['onClick'] = 'handle_infection_instruction()'

                # safe mapping id <-> pk
                self.shifts[id] = shift.pk

    def clean(self):
        super(RegisterForm, self).clean()

        # number of shifts > 0
        number_of_shifts = 0
        infection_instruction_needed = False
        for shift in self.shifts:
            if self.cleaned_data[shift]:
                number_of_shifts += 1

                # while iteration over shifts, check if infection instruction
                # is needed for one of the shifts
                shift_obj = Shift.objects.get(pk=self.shifts[shift])
                if shift_obj.job.infection_instruction:
                    infection_instruction_needed = True

        if number_of_shifts == 0:
            raise ValidationError(_("You must select at least one shift."))

        # infection instruction needed but field not set?
        if infection_instruction_needed and self.cleaned_data['infection_instruction'] == "":
            self.add_error('infection_instruction',
                           _("You must specify, if you have a instruction for the handling of food."))

        # helper need for shift
        for shift in self.shifts:
            if self.cleaned_data[shift]:
                cur_shift = Shift.objects.get(pk=self.shifts[shift])
                if cur_shift.is_full():
                    raise ValidationError("You selected a full shift.")

    def save(self, commit=True):
        instance = super(RegisterForm, self).save()  # must commit

        for shift in self.shifts:
            if self.cleaned_data[shift]:
                new_shift = Shift.objects.get(pk=self.shifts[shift])
                instance.shifts.add(new_shift)

        if commit:
            instance.save()

        return instance

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['admins', 'text', 'imprint', 'registered', ]

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ['name', 'description', 'event', ]

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(JobForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(JobForm, self).save(False)  # event is missing

        # add event
        instance.event = self.event

        if commit:
            instance.save()

        return instance


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        exclude = ['job', ]
        widgets = {
            'begin': forms.DateTimeInput(attrs={'class': 'datetime'}),
            'end': forms.DateTimeInput(attrs={'class': 'datetime'}),
        }

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job')

        super(ShiftForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ShiftForm, self).save(False)  # event is missing

        # add event
        instance.job = self.job

        if commit:
            instance.save()

        return instance

class HelperForm(forms.ModelForm):
    class Meta:
        model = Helper
        exclude = ['shifts', ]

class HelperDeleteForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', 'shifts',]
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

    def delete(self):
        # delete all selected shifts
        for shift in self.cleaned_data['shifts']:
            self.instance.shifts.remove(shift)

        # delete complete helper, if no shifts remain
        if self.instance.shifts.count() == 0:
            self.instance.delete()
