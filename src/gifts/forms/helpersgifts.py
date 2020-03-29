from django import forms
from django.utils.translation import ugettext_lazy as _

from .fields import PresenceField
from ..models import HelpersGifts
from registration.models.helpershift import HelperShift


class HelpersGiftsForm(forms.ModelForm):
    class Meta:
        model = HelpersGifts
        exclude = ['helper', 'deserved_gifts']

    def __init__(self, *args, **kwargs):
        super(HelpersGiftsForm, self).__init__(*args, **kwargs)

        automatic_availability = self.instance.helper.event.giftsettings.enable_automatic_availability

        # remove shift related fields if shirts disabled
        if not self.instance.helper.event.ask_shirt:
            self.fields.pop('got_shirt')
            self.fields.pop('buy_shirt')

        # delivered gift sets
        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)


            helpershift = HelperShift.objects.get(helper=self.instance.helper, shift=giftset.shift)
            missed_shift = not helpershift.present and helpershift.manual_presence

            self.fields[delivered_id_str] = forms.BooleanField(
                label=_("Delivered"),
                required=False,
                initial=giftset.delivered,
                disabled=missed_shift)


        # presence fields per shift
        for helpershift in self.instance.helper.helpershift_set.all():
            present_id_str = "present_{}".format(helpershift.shift.pk)

            self.fields[present_id_str] = PresenceField(
                automatic_availability=automatic_availability,
                helpershift=helpershift)

    def save(self, commit=True):
        instance = super(HelpersGiftsForm, self).save(False)

        # delivered gift sets
        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)

            giftset.delivered = self.cleaned_data[delivered_id_str]
            giftset.save()

        # presence
        for helpershift in self.instance.helper.helpershift_set.all():
            present_id_str = "present_{}".format(helpershift.shift.pk)
            present = self.cleaned_data.get(present_id_str)

            instance.set_present(helpershift.shift, present)

        # and finally store the other flags
        instance = super(HelpersGiftsForm, self).save(True)
        return instance

    def deservedgifts_for_shift(self, shift):
        return self.instance.deservedgiftset_set.filter(shift=shift)
