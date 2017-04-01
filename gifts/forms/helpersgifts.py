from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import HelpersGifts


class HelpersGiftsForm(forms.ModelForm):
    class Meta:
        model = HelpersGifts
        exclude = ['helper', 'deserved_gifts', ]

    def __init__(self, *args, **kwargs):
        super(HelpersGiftsForm, self).__init__(*args, **kwargs)

        if not self.instance.helper.event.ask_shirt:
            self.fields.pop('got_shirt')
            self.fields.pop('buy_shirt')

        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)

            self.fields[delivered_id_str] = forms.BooleanField(
                label=_("Delivered"),
                required=False,
                initial=giftset.delivered)

        for shift in self.instance.helper.shifts.all():
            present_id_str = "present_{}".format(shift.pk)
            self.fields[present_id_str] = forms.BooleanField(
                label=_("Present"),
                required=False,
                initial=self.instance.get_present(shift))

    def save(self, commit=True):
        instance = super(HelpersGiftsForm, self).save(False)

        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)
            #present_id_str = "present_{}".format(giftset.pk)

            giftset.delivered = self.cleaned_data[delivered_id_str]
            giftset.save()

        # must commit for m2m operations
        instance.save()

        for shift in self.instance.helper.shifts.all():
            present_id_str = "present_{}".format(shift.pk)
            instance.set_present(shift, self.cleaned_data[present_id_str])

        return instance

    def deservedgifts_for_shift(self, shift):
        return self.instance.deservedgiftset_set.filter(shift=shift)
