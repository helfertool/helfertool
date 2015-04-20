from django import forms

from .models import Helper

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', 'phone', 'shirt', 'comment']

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        self.shifts = []

        super(RegisterForm, self).__init__(*args, **kwargs)

        for job in event.job_set.all():
            for shift in job.shift_set.all():
                self.fields['shift_%s' % shift.pk] = forms.BooleanField(label=shift, required=False)
                self.shifts.append('shift_%s' % shift.pk)
