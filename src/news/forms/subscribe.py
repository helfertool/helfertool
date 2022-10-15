from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class SubscribeForm(forms.Form):
    """Subscribe to newsletter.

    We do not use a ModelForm here, as we want to implement different behaviour if the mail address exists already.
    Overall, this seems to be easier with a Form.
    """

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
