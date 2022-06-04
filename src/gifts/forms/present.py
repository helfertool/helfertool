from django import forms

from .fields import PresenceField

import logging

logger = logging.getLogger("helfertool.gifts")


class PresentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._shift = kwargs.pop("shift")
        self._user = kwargs.pop("user")

        super(PresentForm, self).__init__(*args, **kwargs)

        self.automatic_presence = self._shift.job.event.giftsettings.enable_automatic_presence

        # first, trigger the auto update for all relevant helpers
        for helpershift in self._shift.helpershift_set.all():
            helpershift.helper.gifts.update()

        # then create the fields (separately, so that we have the new values from the database)
        for helpershift in self._shift.helpershift_set.all():
            id_str = "helper_{}".format(helpershift.helper.pk)

            self.fields[id_str] = PresenceField(automatic_presence=self.automatic_presence, helpershift=helpershift)

    def save(self):
        for helpershift in self._shift.helpershift_set.all():
            id_str = "helper_{}".format(helpershift.helper.pk)
            present = self.cleaned_data.get(id_str)
            helpershift.helper.gifts.set_present(helpershift.shift, present)

            # logging per helper (if changed)
            if id_str in self.changed_data:
                logger.info(
                    "helper presence",
                    extra={
                        "user": self._user,
                        "event": helpershift.helper.event,
                        "helper": helpershift.helper,
                        "shift": helpershift.shift,
                        "present": present,
                    },
                )
