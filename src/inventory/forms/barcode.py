from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..models import Item


class InventoryBarcodeForm(forms.Form):
    barcode = forms.CharField(
        label=_("Barcode"),
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"autofocus": ""}),
    )

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop("event")

        self.item = None

        super(InventoryBarcodeForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(InventoryBarcodeForm, self).__init__()

        barcode = self.cleaned_data.get("barcode")

        # check if badge exists
        try:
            available = self.event.inventory_settings.available_inventory.values("id")
            self.item = Item.objects.get(inventory__in=available, barcode=barcode)
        except Item.DoesNotExist:
            raise ValidationError(_("There is no item with this barcode for " "this event."))
