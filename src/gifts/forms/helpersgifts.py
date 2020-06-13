from django import forms
from django.utils.translation import ugettext_lazy as _

from .fields import PresenceField
from ..models import HelpersGifts

import logging
logger = logging.getLogger("helfertool.gifts")

class HelpersGiftsForm(forms.ModelForm):
    class Meta:
        model = HelpersGifts
        exclude = ['helper', 'deserved_gifts', ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.helper = kwargs.pop('helper')
        super(HelpersGiftsForm, self).__init__(*args, **kwargs)

        automatic_presence = self.instance.helper.event.giftsettings.enable_automatic_presence

        # remove shift related fields if shirts disabled
        if not self.instance.helper.event.ask_shirt:
            self.fields.pop('got_shirt')
            self.fields.pop('buy_shirt')

        # delivered gift sets
        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)

            missed_shift = self.instance.helper.has_missed_shift(giftset.shift)

            self.fields[delivered_id_str] = forms.BooleanField(
                label=_("Delivered"),
                required=False,
                initial=giftset.delivered,
                disabled=missed_shift)

        # presence fields per shift
        for helpershift in self.instance.helper.helpershift_set.all():
            present_id_str = "present_{}".format(helpershift.shift.pk)

            self.fields[present_id_str] = PresenceField(
                automatic_presence=automatic_presence,
                helpershift=helpershift)

    def save(self, commit=True):
        instance = super(HelpersGiftsForm, self).save(False)

        # delivered gift sets
        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)

            if commit:
                gifts = { gift.gift.id : gift.count for gift in giftset.gifts }
                logger.info("giftset delivered", extras={
                    'user': self.user,
                    'helper': self.helper,
                    'event': self.helper.event,
                    'giftset': giftset,
                    'gifts': gifts,
                })

            giftset.delivered = self.cleaned_data[delivered_id_str]
            giftset.save()

        # presence
        for helpershift in self.instance.helper.helpershift_set.all():
            present_id_str = "present_{}".format(helpershift.shift.pk)
            present = self.cleaned_data.get(present_id_str)

            logstr = "helper present" if present else "helper absent"
            logger.info(logstr, extras={
                'user': self.user,
                'helper': self.helper,
                'event': self.helper.event,
                'shift': helpershift,
            })

            instance.set_present(helpershift.shift, present)

        # and finally store the other flags
        instance = super(HelpersGiftsForm, self).save(commit)
        return instance

    def deservedgifts_for_shift(self, shift):
        return self.instance.deservedgiftset_set.filter(shift=shift)
