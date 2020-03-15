from django import forms

from .fields import PresenceField


class PresentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.shift = kwargs.pop('shift')

        super(PresentForm, self).__init__(*args, **kwargs)

        self.automatic_presence = self.shift.job.event.giftsettings.enable_automatic_presence

        for helpershift in self.shift.helpershift_set.all():
            # first, trigger the auto update
            helpershift.helper.gifts.update()

            # then add field
            id_str = "helper_{}".format(helpershift.helper.pk)

            self.fields[id_str] = PresenceField(
                automatic_presence=self.automatic_presence,
                helpershift=helpershift)

    def save(self):
        for helpershift in self.shift.helpershift_set.all():
            id_str = "helper_{}".format(helpershift.helper.pk)
            present = self.cleaned_data.get(id_str)
            helpershift.helper.gifts.set_present(helpershift.shift, present)
