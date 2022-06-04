from django import forms

from ..models import GiftSettings


class GiftSettingsForm(forms.ModelForm):
    class Meta:
        model = GiftSettings
        exclude = [
            "event",
        ]

    def __init__(self, *args, **kwargs):
        super(GiftSettingsForm, self).__init__(*args, **kwargs)

        if self.instance.event.archived:
            for field_id in self.fields:
                self.fields[field_id].disabled = True
