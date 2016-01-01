from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import Badge


class RegisterBadgeForm(forms.Form):
    badge_id = forms.IntegerField(label='Barcode',
                                  widget=forms.TextInput(
                                    attrs={'autofocus': ''}))

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        self.badge = None

        super(RegisterBadgeForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(RegisterBadgeForm, self).__init__()

        id = self.cleaned_data.get('badge_id')

        # check if id is given
        if not id:
            raise ValidationError(_("Invalid barcode."))

        # check if badge exists
        try:
            self.badge = Badge.objects.get(pk=id)
        except Badge.DoesNotExist:
            raise ValidationError(_("This badge does not exist. "
                                    "Maybe it was deleted since printing."))

        # check if badge belongs to event
        if self.badge.helper.event != self.event:
            raise ValidationError(_("This badge does not belong to this "
                                    "event."))
