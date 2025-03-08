from django import forms
from django.conf import settings
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from captcha.fields import CaptchaField
from helfertool.forms import CustomCaptchaTextInput


class SubscribeForm(forms.Form):
    """Subscribe to newsletter.

    We do not use a ModelForm here, as we want to implement different behaviour if the mail address exists already.
    Overall, this seems to be easier with a Form.
    """

    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)

        if not settings.CAPTCHAS_NEWSLETTER:
            self.fields.pop("captcha")

    email = forms.EmailField(
        label=_("E-Mail"),
        required=True,
    )

    privacy_statement = forms.BooleanField(
        label=format_html(
            '{} (<a href="" data-bs-toggle="modal" data-bs-target="#privacy">{}</a>)',
            _("I agree with the data privacy statement."),
            _("Show"),
        ),
        error_messages={"required": _("You have to accept the data privacy statement.")},
        required=True,
    )

    captcha = CaptchaField(widget=CustomCaptchaTextInput)
