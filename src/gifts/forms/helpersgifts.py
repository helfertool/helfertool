from django import forms
from django.utils.translation import ugettext_lazy as _

from .fields import PresenceField
from ..models import HelpersGifts


class HelpersGiftsForm(forms.ModelForm):
    class Meta:
        model = HelpersGifts
        exclude = ['helper', 'deserved_gifts', ]

    def __init__(self, *args, **kwargs):
        gifts_readonly = kwargs.pop("gifts_readonly", False)
        presence_readonly = kwargs.pop("presence_readonly", False)

        super(HelpersGiftsForm, self).__init__(*args, **kwargs)

        automatic_presence = self.instance.helper.event.giftsettings.enable_automatic_presence

        # delivered gift sets
        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)

            missed_shift = self.instance.helper.has_missed_shift(giftset.shift)

            # field should be disabled if the helper missed the shift and it is not delivered
            # -> we can remove the delivered flags for missed shifts, but not add it
            # additionally: if gifts are read-only
            disabled = (missed_shift and not giftset.delivered) or gifts_readonly

            self.fields[delivered_id_str] = forms.BooleanField(
                label=_("Delivered"),
                required=False,
                initial=giftset.delivered,
                disabled=disabled)

        # presence fields per shift
        for helpershift in self.instance.helper.helpershift_set.all():
            present_id_str = "present_{}".format(helpershift.shift.pk)

            self.fields[present_id_str] = PresenceField(
                automatic_presence=automatic_presence,
                helpershift=helpershift,
                disabled=presence_readonly)

        # disable gift related fields if gifts are read-only
        # (do this before possible removing some of them in the next code block)
        if gifts_readonly:
            self.fields['deposit'].disabled = True
            self.fields['deposit_returned'].disabled = True
            self.fields['got_shirt'].disabled = True
            self.fields['buy_shirt'].disabled = True

        # remove shirt related fields if shirts disabled
        if not self.instance.helper.event.ask_shirt:
            self.fields.pop('got_shirt')
            self.fields.pop('buy_shirt')

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
        instance = super(HelpersGiftsForm, self).save(commit)
        return instance

    def deservedgifts_for_shift(self, shift):
        return self.instance.deservedgiftset_set.filter(shift=shift)
