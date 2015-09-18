from django import forms

from ..models import BadgeDesign


class BadgeDesignForm(forms.ModelForm):
    class Meta:
        model = BadgeDesign
        exclude = []
