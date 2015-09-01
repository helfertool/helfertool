from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import formats, translation
from django.utils.translation import ugettext_lazy as _

from .models import Helper, Shift, Event, Job

class RegisterForm(forms.ModelForm):
    """ Form for registration of helpers.

    This form asks for the personal data and handles the selection of shifts.
    There is a BooleanField for each shift. clean() does the validation and
    save() handles the shifts.
    """
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', 'phone', 'shirt', 'vegetarian', 'infection_instruction', 'comment']

    def __init__(self, *args, **kwargs):
        """ Customize the form.

        The fields 'shirt' and 'vegetarian' are removed, if they are not
        necessary. Then the custom fields for the shifts are created.
        """
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
        for job in event.public_jobs:
            for shift in job.shift_set.all():
                id = 'shift_%s' % shift.pk
                self.fields[id] = forms.BooleanField(label=shift,
                                                     required=False)

                # disable button if shift is full
                if shift.is_full() or shift.blocked:
                    self.fields[id].widget.attrs['disabled'] = True

                # set class if infection instruction is needed for this shift
                if shift.job.infection_instruction:
                    self.fields[id].widget.attrs['class'] = 'infection_instruction'
                    self.fields[id].widget.attrs['onClick'] = 'handle_infection_instruction()'

                # safe mapping id <-> pk
                self.shifts[id] = shift.pk

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
                if cur_shift.blocked:
                    raise ValidationError("You selected a blocked shift.")

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
        exclude = ['text', 'imprint', 'registered', ]
        widgets = {
            'admins': forms.SelectMultiple(attrs={'class': 'duallistbox'}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ['name', 'description', 'event', 'coordinators']
        widgets = {
            'job_admins': forms.SelectMultiple(attrs={'class': 'duallistbox'}),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(JobForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(JobForm, self).save(False)  # event is missing

        # add event
        instance.event = self.event

        if commit:
            instance.save()

        self.save_m2m() # save m2m, otherwise job_admins is lost

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

    def clean(self):
        super(ShiftForm, self).clean()

        if self.cleaned_data['begin'] > self.cleaned_data['end']:
            raise ValidationError(_("The begin of the shift must be before "
                                    "the end."))

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

    def __init__(self, *args, **kwargs):
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

        if commit:
            instance.save()

        if self.shift:
            instance.shifts.add(self.shift)
            self.save_m2m()

        if self.job:
            self.job.coordinators.add(self.instance)

        return instance


class UsernameForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=100, required=False)

    instance = None

    def clean(self):
        cleaned_data = super(UsernameForm, self).clean()
        username = cleaned_data.get("username")

        # search for user
        if username:
            try:
                self.instance = User.objects.get(username=username)
            except User.DoesNotExist as e:
                raise forms.ValidationError(_("The user does not exist."))

    def get_user(self):
        return self.instance

class UserCreationForm(UserCreationForm):
    email = forms.EmailField(label=_("Email address"), required=True)
    first_name = forms.CharField(label=_('First name'), max_length=30,
                                 required=True)
    last_name = forms.CharField(label=_('Last name'), max_length=30,
                                required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1",
                  "password2")

    def clean(self):
        # add '@' to the beginning
        if not self.cleaned_data['username'].startswith('@'):
            self.cleaned_data['username'] = '@' + self.cleaned_data['username']

        return super(UserCreationForm, self).clean()

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)

        # change mail and name
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user

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

    def get_deleted_shifts(self):
        return self.cleaned_data['shifts']

    def delete(self):
        # delete all selected shifts
        for shift in self.cleaned_data['shifts']:
            self.instance.shifts.remove(shift)

        # delete complete helper, if no shifts remain
        if self.instance.shifts.count() == 0:
            self.instance.delete()

class ShiftDeleteForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = []

    def delete(self):
        self.instance.delete()

class JobDeleteForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = []

    def delete(self):
        self.instance.delete()

class EventDeleteForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = []

    def delete(self):
        self.instance.delete()

class DeleteForm(forms.Form):
    pass
