from django import forms

from ..models import CoronaSettings


class CoronaSettingsForm(forms.ModelForm):
    class Meta:
        model = CoronaSettings
        exclude = [
            "event",
        ]

    def __init__(self, *args, **kwargs):
        super(CoronaSettingsForm, self).__init__(*args, **kwargs)

        if self.instance.event.archived:
            for field_id in self.fields:
                self.fields[field_id].disabled = True
