from django import forms
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ..models import Person


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)

        # error message for existing mail address
        self.fields['email'].error_messages['unique'] = _("You subscribed already to the newsletter.")

        # privacy statement
        privacy_label = format_html(
            '{} (<a href="" data-bs-toggle="collapse" data-bs-target="#privacy">{}</a>)',
            _("I agree with the data privacy statement."),
            _("Show"),
        )
        privacy_error = _("You have to accept the data privacy statement.")

        self.fields['privacy_statement'] = forms.BooleanField(
            label=privacy_label,
            required=True,
            error_messages={'required': privacy_error},
        )

    def save(self, commit=True):
        instance = super(SubscribeForm, self).save(False)

        instance.withevent = False

        if commit:
            instance.save()
