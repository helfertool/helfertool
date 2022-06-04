from django import forms

from ..models import Gift


class GiftForm(forms.ModelForm):
    class Meta:
        model = Gift
        exclude = [
            "name",
            "event",
        ]

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop("event")

        super(GiftForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(GiftForm, self).save(False)

        instance.event = self.event

        if commit:
            instance.save()

        return instance


class GiftDeleteForm(forms.ModelForm):
    class Meta:
        model = Gift
        fields = []

    def delete(self):
        self.instance.delete()
