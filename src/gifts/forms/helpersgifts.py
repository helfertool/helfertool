from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import HelpersGifts


class HelpersGiftsForm(forms.ModelForm):
    class Meta:
        model = HelpersGifts
        exclude = ['helper', 'deserved_gifts']

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

        CHOICES = [('auto', _('Auto')),
                   ('present', _('Present')),
                   ('absent', _('Absent'))]

        for helpershift in self.instance.helper.helpershift_set.all():
            shift = helpershift.shift
            present_id_str = "present_{}".format(shift.pk)

            if helpershift.present:
                initial = "present"
            else:
                if helpershift.manual_presence:
                    initial = "absent"
                else:
                    initial = "auto"

            self.fields[present_id_str] = forms.ChoiceField(
                initial=initial,
                choices=CHOICES,
                widget=forms.RadioSelect)

    def save(self, commit=True):
        instance = super(HelpersGiftsForm, self).save(False)

        for giftset in self.instance.deservedgiftset_set.all():
            delivered_id_str = "delivered_{}".format(giftset.pk)

            giftset.delivered = self.cleaned_data[delivered_id_str]
            giftset.save()

        # must commit for m2m operations
        instance.save()

        for helpershift in self.instance.helper.helpershift_set.all():
            shift = helpershift.shift
            present_id_str = "present_{}".format(shift.pk)
            present = self.cleaned_data.get(present_id_str)

            if present == 'present':
                instance.set_present(shift, True)
            elif present == 'absent':
                instance.set_present(shift, False)
            elif present == 'auto':
                instance.set_present(shift, None)

        return instance

    def deservedgifts_for_shift(self, shift):
        return self.instance.deservedgiftset_set.filter(shift=shift)
