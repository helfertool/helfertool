from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import HelpersGifts, DeservedGiftSet


class HelpersGiftsForm(forms.ModelForm):
    class Meta:
        model = HelpersGifts
        exclude = ['helper', 'deserved_gifts', ]

    def __init__(self, *args, **kwargs):
        super(HelpersGiftsForm, self).__init__(*args, **kwargs)

        self._gifts = {}

        for gifts in self.instance.deservedgiftset_set.all():
            id_str = "gift_{}".format(gifts.pk)

            self.fields[id_str] = forms.BooleanField(label=_("Delivered"),
                                                     required=False,
                                                     initial=gifts.delivered)
            self._gifts[id_str] = gifts.pk

    def save(self, commit=True):
        instance = super(HelpersGiftsForm, self).save(False)

        for id_str in self._gifts:
            tmp = DeservedGiftSet.objects.get(pk=self._gifts[id_str])
            tmp.delivered = self.cleaned_data[id_str]
            tmp.save()

        if commit:
            instance.save()

        return instance

    def deservedgifts_for_shift(self, shift):
        return self.instance.deservedgiftset_set.filter(shift=shift)
