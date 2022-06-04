from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings

from ..models import SpecialBadges


class SpecialBadgesForm(forms.ModelForm):
    class Meta:
        model = SpecialBadges
        fields = ["name", "number"]

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop("event")

        super(SpecialBadgesForm, self).__init__(*args, **kwargs)

    def clean_number(self):
        number = self.cleaned_data["number"]
        if number > settings.BADGE_SPECIAL_MAX:
            raise ValidationError("Maximum number is %(max)d", params={"max": settings.BADGE_SPECIAL_MAX})
        return number

    def save(self, commit=True):
        instance = super(SpecialBadgesForm, self).save(False)

        instance.event = self.event

        if commit:
            instance.save()

        self.save_m2m()

        return instance


class SpecialBadgesDeleteForm(forms.ModelForm):
    class Meta:
        model = SpecialBadges
        fields = []

    def delete(self):
        self.instance.delete()
