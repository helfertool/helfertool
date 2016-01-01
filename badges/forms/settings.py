from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import magic

from ..models import BadgeSettings


class BadgeSettingsForm(forms.ModelForm):
    class Meta:
        model = BadgeSettings
        exclude = ['event', 'defaults', ]

    def clean_latex_template(self):
        file = self.cleaned_data['latex_template']

        # check mimetype with libmagic
        filemime = magic.from_buffer(file.read(), mime=True)
        if filemime != b'text/x-tex':
            raise ValidationError(_("File does not contain LaTeX code."))

        # seek to begin (may be necessary for further use?)
        file.seek(0)

        return file
