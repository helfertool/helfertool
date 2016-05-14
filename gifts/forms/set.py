from django import forms

from ..models import GiftSet


class GiftSetForm(forms.ModelForm):
    class Meta:
        model = GiftSet
        exclude = ['name', 'event', ]

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(GiftSetForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(GiftSetForm, self).save(False)

        instance.event = self.event

        if commit:
            instance.save()

        return instance
