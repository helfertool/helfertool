from django import forms
from django.conf import settings

from ..models import HTMLSetting, TextSetting


class HTMLSettingForm(forms.ModelForm):
    class Meta:
        model = HTMLSetting
        exclude = [
            "key",
            "value",
        ]

    def __init__(self, *args, **kwargs):
        super(HTMLSettingForm, self).__init__(*args, **kwargs)

        # form label should only contain language
        for lang, name in settings.LANGUAGES:
            self.fields["value_{}".format(lang)].label = name


class TextSettingForm(forms.ModelForm):
    class Meta:
        model = TextSetting
        exclude = [
            "key",
            "value",
        ]

    def __init__(self, *args, **kwargs):
        super(TextSettingForm, self).__init__(*args, **kwargs)

        # form label should only contain language
        for lang, name in settings.LANGUAGES:
            self.fields["value_{}".format(lang)].label = name
