from django import forms
from django.conf import settings

from ckeditor.widgets import CKEditorWidget

from ..models import HTMLSetting, TextSetting


class HTMLSettingForm(forms.ModelForm):
    class Meta:
        model = HTMLSetting
        exclude = ['key', 'value', ]

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        widgets = {}
        for lang, name in settings.LANGUAGES:
            widgets["value_{}".format(lang)] = CKEditorWidget()


class TextSettingForm(forms.ModelForm):
    class Meta:
        model = TextSetting
        exclude = ['key', 'value', ]
