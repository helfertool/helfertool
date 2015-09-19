from django import forms

from ..models import BadgeDesign, BadgeSettings


class BadgeSettingsForm(forms.ModelForm):
    class Meta:
        model = BadgeSettings
        exclude = ['event', 'design', ]


class BadgeDesignForm(forms.ModelForm):
    class Meta:
        model = BadgeDesign
        exclude = []
