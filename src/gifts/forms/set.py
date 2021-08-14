from django import forms

from ..models import Gift, GiftSet


class GiftSetForm(forms.ModelForm):
    class Meta:
        model = GiftSet
        exclude = ['name', 'event', 'gifts', ]

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(GiftSetForm, self).__init__(*args, **kwargs)

        available_gifts = Gift.objects.filter(event=self.event)
        self.gift_form_ids = {}

        for gift in available_gifts:
            gift_id = "gift_{}".format(gift.pk)
            self.gift_form_ids[gift.pk] = gift_id

            number = 0
            if self.instance:
                number = self.instance.get_gift_num(gift)

            self.fields[gift_id] = forms.IntegerField(label=gift.name,
                                                      required=False,
                                                      min_value=0,
                                                      initial=number)

    def save(self, commit=True):
        instance = super(GiftSetForm, self).save(False)

        instance.event = self.event

        instance.save()  # must commit

        available_gifts = Gift.objects.filter(event=self.event)
        for gift in available_gifts:
            form_id = self.gift_form_ids.get(gift.pk)
            if form_id and form_id in self.cleaned_data:
                number = self.cleaned_data[form_id]
                self.instance.set_gift_num(gift, number)

        return instance


class GiftSetDeleteForm(forms.ModelForm):
    class Meta:
        model = GiftSet
        fields = []

    def delete(self):
        self.instance.delete()
