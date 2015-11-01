from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import Helper, Shift

import itertools


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
        self.displayed_shifts = kwargs.pop('shifts')
        self.shifts = {}

        super(RegisterForm, self).__init__(*args, **kwargs)

        # remove field for shirt?
        if not self.event.ask_shirt:
            self.fields.pop('shirt')

        # remove field for vegetarian food?
        if not self.event.ask_vegetarian:
            self.fields.pop('vegetarian')

        # get a list of all shifts
        if self.displayed_shifts:
            all_shifts = self.displayed_shifts
        else:
            all_shifts = Shift.objects.filter(job__event=self.event)

        # add fields for shifts
        for shift in all_shifts:
            id = 'shift_%s' % shift.pk
            self.fields[id] = forms.BooleanField(label=shift,
                                                 required=False)

            # disable button if shift is full
            if shift.is_full() or (shift.blocked and not
                                   self.displayed_shifts):
                self.fields[id].widget.attrs['disabled'] = True

            # set class if infection instruction is needed for this shift
            if shift.job.infection_instruction:
                self.fields[id].widget.attrs['class'] = 'infection_instruction'
                self.fields[id].widget.attrs['onClick'] = \
                    'handle_infection_instruction()'

            # safe mapping id <-> pk
            self.shifts[id] = shift.pk

    def get_jobs(self):
        if self.displayed_shifts:
            jobs = []

            # get all jobs, that have a shift contained in displayed_shifts
            for job in self.event.job_set.all():
                if job.shift_set.all() & self.displayed_shifts.all():
                    jobs.append(job)
            return jobs
        else:
            return self.event.public_jobs

    def get_shifts(self, job):
        if self.displayed_shifts:
            shifts = self.displayed_shifts.filter(job=job)
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

        TODO: improve performance: get shift only once from DB
        """
        super(RegisterForm, self).clean()

        number_of_shifts = 0
        infection_instruction_needed = False

        selected_shifts = list(filter(lambda s: self.cleaned_data[s],
                                      self.shifts))

        # iterate over all (selected) shifts
        for shift in selected_shifts:
            # get this shift
            cur_shift = Shift.objects.get(pk=self.shifts[shift])

            # number of shifts
            number_of_shifts += 1

            # check if infection instruction is needed for one of the
            # shifts
            if cur_shift.job.infection_instruction:
                infection_instruction_needed = True

            # check if shift is full
            if cur_shift.is_full():
                raise ValidationError(_("You selected a full shift."))

            # check if shift is blocked
            if cur_shift.blocked and not self.displayed_shifts:
                raise ValidationError(_("You selected a blocked shift."))

        # check number of shifts > 0
        if number_of_shifts == 0:
            raise ValidationError(_("You must select at least one shift."))

        # infection instruction needed but field not set?
        if (infection_instruction_needed and
                self.cleaned_data['infection_instruction'] == ""):
            self.add_error('infection_instruction',
                           _("You must specify, if you have a instruction for "
                             "the handling of food."))

        # check for overlapping shifts
        if self.event.max_overlapping:
            max = self.event.max_overlapping
            for shifts in itertools.combinations(selected_shifts, 2):
                s1 = Shift.objects.get(pk=self.shifts[shifts[0]])
                s2 = Shift.objects.get(pk=self.shifts[shifts[1]])

                # check if shifts overlap (1st or term) or one shift is part
                # of the other shift (2nd and 3rd or term)
                if ((s2.end-s1.begin).total_seconds() > max*60 and
                    (s1.end-s2.begin).total_seconds() > max*60) or \
                   (s1.begin >= s2.begin and s1.end <= s2.end) or \
                   (s2.begin >= s1.begin and s2.end <= s1.end):
                    raise ValidationError(
                        _("Some of your shifts overlap more then "
                          "%(minutes)d minutes.") %
                        {'minutes': max})

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
