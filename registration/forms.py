from django import forms
from django.core.exceptions import ValidationError

from .models import Helper, Shift

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', 'phone', 'shirt', 'vegetarian', 'infection_instruction', 'comment']

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        self.shifts = {}

        super(RegisterForm, self).__init__(*args, **kwargs)

        for job in event.job_set.all():
            for shift in job.shift_set.all():
                id = 'shift_%s' % shift.pk
                self.fields[id] = forms.BooleanField(label=shift, required=False)
                if shift.is_full():
                    self.fields[id].widget.attrs['disabled'] = True
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
            raise ValidationError("Es muss mindestens eine Schicht gewählt sein")

        # infection instruction needed but field not set?
        if infection_instruction_needed and self.cleaned_data['infection_instruction'] == "":
            self.add_error('infection_instruction', "Es muss angegeben werden, \
                           ob eine Gesundheitsbelehrung vorhanden ist")

        # helper need for shift
        for shift in self.shifts:
            if self.cleaned_data[shift]:
                cur_shift = Shift.objects.get(pk=self.shifts[shift])
                if cur_shift.is_full():
                    raise ValidationError("Es wurde eine volle Schicht ausgewählt")

    def save(self, commit=True):
        instance = super(RegisterForm, self).save()  # must commit

        for shift in self.shifts:
            if self.cleaned_data[shift]:
                new_shift = Shift.objects.get(pk=self.shifts[shift])
                instance.shifts.add(new_shift)

        if commit:
            instance.save()

        return instance
