from django import forms

from ..models import GiftSettings


class GiftSettingsForm(forms.ModelForm):
    class Meta:
        model = GiftSettings
        exclude = ['event', ]
