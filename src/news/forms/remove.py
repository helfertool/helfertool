from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Person


class RemoveForm(forms.Form):
    email = forms.EmailField(
        label=_("E-Mail"),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]

        try:
            self.person = Person.objects.get(email=email)
        except Person.DoesNotExist:
            raise forms.ValidationError(_("Unknown e-mail address"))

        return email

    def delete(self):
        email = self.person.email

        self.person.delete()

        return email
