from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from helfertool.forms import DatePicker

from ..models import Agreement, UserAgreement


class AgreementForm(forms.ModelForm):
    class Meta:
        model = Agreement

        exclude = ["name", "text"]

        widgets = {
            "start": DatePicker,
            "end": DatePicker,
        }

    def __init__(self, *args, **kwargs):
        super(AgreementForm, self).__init__(*args, **kwargs)

        # set better label for description fields
        for lang, name in settings.LANGUAGES:
            self.fields["text_{}".format(lang)].label = _("Text (%(lang)s)") % {"lang": name}


class UserAgreementForm(forms.ModelForm):
    class Meta:
        model = UserAgreement
        fields = []
