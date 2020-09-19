from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import Badge


class BadgeBarcodeForm(forms.Form):
    badge_barcode = forms.IntegerField(label=_("Barcode"),
                                       widget=forms.TextInput(
                                       attrs={'autofocus': ''}))

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        self.badge = None

        super(BadgeBarcodeForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(BadgeBarcodeForm, self).__init__()

        barcode = self.cleaned_data.get('badge_barcode')

        # check if id is given
        if not barcode:
            raise ValidationError(_("Invalid barcode."))

        # check if badge exists
        try:
            self.badge = Badge.objects.get(event=self.event, barcode=barcode)
        except Badge.DoesNotExist:
            raise ValidationError(_("This badge does not exist. "
                                    "Maybe it was deleted since printing or "
                                    "does not belong to this event."))
