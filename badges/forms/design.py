from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import BadgeDesign

from ..utils import is_image


class BadgeDesignForm(forms.ModelForm):
    class Meta:
        model = BadgeDesign
        exclude = ['badge_settings', 'name', ]

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings')

        super(BadgeDesignForm, self).__init__(*args, **kwargs)

    def clean_bg_front(self):
        file = self.cleaned_data['bg_front']
        if file and not is_image(file):
            raise ValidationError(_("The file is not an image."))
        return file

    def clean_bg_back(self):
        file = self.cleaned_data['bg_back']
        if file and not is_image(file):
            raise ValidationError(_("The file is not an image."))
        return file

    def save(self, commit=True):
        instance = super(BadgeDesignForm, self).save(False)

        # set settings
        instance.badge_settings = self.settings

        if commit:
            instance.save()

        return instance


class BadgeDesignDeleteForm(forms.ModelForm):
    class Meta:
        model = BadgeDesign
        fields = []

    def delete(self):
        self.instance.delete()
