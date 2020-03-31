from django import forms
from django.utils.translation import ugettext as _


class ShiftTemplateUploadForm(forms.Form):
    update_existing = forms.BooleanField(
        label=_("Update existing shifts"),
        initial=True,
        required=False)
    importform = forms.FileField(label=_("Template file"))
