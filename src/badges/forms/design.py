from django import forms
from django.urls import reverse

from helfertool.forms import ImageFileInput

from ..models import BadgeDesign


class BadgeDesignForm(forms.ModelForm):
    class Meta:
        model = BadgeDesign
        exclude = ['badge_settings', 'name', ]
        widgets = {
            "bg_front": ImageFileInput,
            "bg_back": ImageFileInput,
        }

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings')

        super(BadgeDesignForm, self).__init__(*args, **kwargs)

        # set download_url parameters for widgets
        url_args = [self.instance.get_event().url_name, self.instance.pk]
        self.fields["bg_front"].widget.download_url = reverse("badges:get_design_bg", args=url_args + ["front"])
        self.fields["bg_back"].widget.download_url = reverse("badges:get_design_bg", args=url_args + ["back"])

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
