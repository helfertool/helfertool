from django import forms
from django.conf import settings

from ckeditor.widgets import CKEditorWidget

from registration.forms.fields import DatePicker

from ..models import Agreement, UserAgreement


class AgreementForm(forms.ModelForm):
    class Meta:
        model = Agreement

        exclude = ['name', 'text']

        widgets = {
            'start': DatePicker,
            'end': DatePicker,
        }

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        for lang, name in settings.LANGUAGES:
            widgets["text_{}".format(lang)] = CKEditorWidget()


class UserAgreementForm(forms.ModelForm):
    class Meta:
        model = UserAgreement
        fields = []
