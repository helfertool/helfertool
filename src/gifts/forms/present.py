from django import forms


class PresentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.shift = kwargs.pop('shift')

        super(PresentForm, self).__init__(*args, **kwargs)

        CHOICES = [('auto', ''),
                   ('present', ''),
                   ('absent', '')]

        for helpershift in self.shift.helpershift_set.all():
            helper = helpershift.helper
            id_str = "helper_{}".format(helper.pk)

            if helpershift.present:
                initial = "present"
            else:
                if helpershift.manual_presence:
                    initial = "absent"
                else:
                    initial = "auto"

            self.fields[id_str] = forms.ChoiceField(
                initial=initial,
                label=helper.full_name,
                choices=CHOICES,
                widget=forms.RadioSelect)

    def save(self):
        for helper in self.shift.helper_set.all():
            id_str = "helper_{}".format(helper.pk)

            present = self.cleaned_data.get(id_str)

            if present == 'present':
                helper.gifts.set_present(self.shift, True)
            elif present == 'absent':
                helper.gifts.set_present(self.shift, False)
            elif present == 'auto':
                helper.gifts.set_present(self.shift, None)