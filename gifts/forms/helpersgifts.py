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
            present_id_str = "present_{}".format(giftset.pk)

            self.fields[delivered_id_str] = forms.BooleanField(
                label=_("Delivered"),
                required=False,
                initial=giftset.delivered)

            self.fields[present_id_str] = forms.BooleanField(
                label=_("Present"),
                required=False,
                initial=giftset.present)

    def save(self, commit=True):
        instance = super(HelpersGiftsForm, self).save(False)

        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)
            present_id_str = "present_{}".format(giftset.pk)

            giftset.delivered = self.cleaned_data[delivered_id_str]
            giftset.present = self.cleaned_data[present_id_str]
            giftset.save()

        if commit:
            instance.save()

        return instance

    def deservedgifts_for_shift(self, shift):
        return self.instance.deservedgiftset_set.filter(shift=shift)
