from django import forms
from django.utils.translation import ugettext_lazy as _


class PresentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.shift = kwargs.pop('shift')

        super(PresentForm, self).__init__(*args, **kwargs)

        for helper in self.shift.helper_set.all():
            id_str = "helper_{}".format(helper.pk)

            self.fields[id_str] = forms.BooleanField(
                label=_(helper.full_name),
                required=False,
                initial=helper.gifts.get_present(self.shift))

    def save(self):
        for helper in self.shift.helper_set.all():
            id_str = "helper_{}".format(helper.pk)

            present = self.cleaned_data.get(id_str)
            helper.gifts.set_present(self.shift, present)
