from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from ..models import ContactTracingData


class ContactTracingDataForm(forms.ModelForm):
    class Meta:
        model = ContactTracingData
        exclude = [
            "event",
            "helper",
        ]

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop("event")

        super(ContactTracingDataForm, self).__init__(*args, **kwargs)

        self.fields["country"].initial = settings.DEFAULT_COUNTRY

    def clean(self):
        super(ContactTracingDataForm, self).clean()

        if not self.cleaned_data.get("agreed"):
            self.add_error("agreed", _("You have to provide correct data."))

    def save(self, helper, commit=True):
        instance = super(ContactTracingDataForm, self).save(False)
        instance.event = self.event
        instance.helper = helper

        if commit:
            instance.save()

        return instance
