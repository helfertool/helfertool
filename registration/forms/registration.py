from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import Helper, Shift


class RegisterForm(forms.ModelForm):
    """ Form for registration of helpers.

    This form asks for the personal data and handles the selection of shifts.
    There is a BooleanField for each shift. clean() does the validation and
    save() handles the shifts.
    """
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', 'phone', 'shirt',
                  'vegetarian', 'infection_instruction', 'comment']

    def __init__(self, *args, **kwargs):
        """ Customize the form.

        The fields 'shirt' and 'vegetarian' are removed, if they are not
        necessary. Then the custom fields for the shifts are created.
        """
        self.event = kwargs.pop('event')
        self.link = kwargs.pop('link')
        self.shifts = {}

        super(RegisterForm, self).__init__(*args, **kwargs)

        # remove field for shirt?
        if not self.event.ask_shirt:
            self.fields.pop('shirt')

        # remove field for vegetarian food?
        if not self.event.ask_vegetarian:
            self.fields.pop('vegetarian')

        # get a list of all shifts
        if self.link:
            all_shifts = self.link.shifts.all()
        else:
            all_shifts = Shift.objects.filter(job__event=self.event)

        # add fields for shifts
        for shift in all_shifts:
            id = 'shift_%s' % shift.pk
            self.fields[id] = forms.BooleanField(label=shift,
                                                 required=False)

            # disable button if shift is full
            if shift.is_full() or (shift.blocked and not self.link):
                self.fields[id].widget.attrs['disabled'] = True

            # set class if infection instruction is needed for this shift
            if shift.job.infection_instruction:
                self.fields[id].widget.attrs['class'] = 'infection_instruction'
                self.fields[id].widget.attrs['onClick'] = \
                    'handle_infection_instruction()'

            # safe mapping id <-> pk
            self.shifts[id] = shift.pk

    def get_jobs(self):
        if self.link:
            jobs = []

            # get all jobs, that have a shift contained in link.shifts
            for job in self.event.job_set.all():
                if job.shift_set.all() & self.link.shifts.all():
                    jobs.append(job)
            return jobs
        else:
            return self.event.public_jobs

    def get_shifts(self, job):
        if self.link:
            shifts = self.link.shifts.filter(job=job)
            return job.shifts_by_day(shifts)
        else:
            return job.shifts_by_day()

    def clean(self):
        """ Custom validation of shifts and other fields.

        This method performs some validations:
          * The helper must register for at least one shift.
          * The field 'infection_instruction' must be set, if one of the
            selected shifts requires this.
          * The selected shift is not full.
        """
        super(RegisterForm, self).clean()

        # number of shifts > 0
        number_of_shifts = 0
        infection_instruction_needed = False
        for shift in self.shifts:
            if self.cleaned_data[shift]:
                number_of_shifts += 1

                # while iterating over shifts, check if infection instruction
                # is needed for one of the shifts
                shift_obj = Shift.objects.get(pk=self.shifts[shift])
                if shift_obj.job.infection_instruction:
                    infection_instruction_needed = True

        if number_of_shifts == 0:
            raise ValidationError(_("You must select at least one shift."))

        # infection instruction needed but field not set?
        if (infection_instruction_needed and
                self.cleaned_data['infection_instruction'] == ""):
            self.add_error('infection_instruction',
                           _("You must specify, if you have a instruction for "
                             "the handling of food."))

        # helper need for shift
        for shift in self.shifts:
            if self.cleaned_data[shift]:
                cur_shift = Shift.objects.get(pk=self.shifts[shift])
                if cur_shift.is_full():
                    raise ValidationError("You selected a full shift.")
                if cur_shift.blocked and not self.link:
                    raise ValidationError("You selected a blocked shift.")

    def save(self, commit=True):
        instance = super(RegisterForm, self).save(False)

        instance.event = self.event

        # must commit for m2m operations
        instance.save()

        for shift in self.shifts:
            if self.cleaned_data[shift]:
                new_shift = Shift.objects.get(pk=self.shifts[shift])
                instance.shifts.add(new_shift)

        if commit:
            instance.save()

        return instance
