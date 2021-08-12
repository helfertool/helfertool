from django import forms
from django.utils.translation import ugettext_lazy as _

from helfertool.forms import UserSelectWidget

from ..models import Item, Inventory


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        exclude = []
        widgets = {
            'admins': UserSelectWidget,
        }


class InventoryDeleteForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = []

    def delete(self):
        self.instance.delete()


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ['inventory', ]

    def __init__(self, *args, **kwargs):
        self.inventory = kwargs.pop('inventory')

        super(ItemForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # check that barcode is unique for this inventory (not done by default since inventory is excluded)
        try:
            existing = Item.objects.get(barcode=cleaned_data.get("barcode"), inventory=self.inventory)
            if not self.instance.pk or existing.pk != self.instance.pk:
                self.add_error("barcode", _("Item with this barcode already exists in this inventory"))
        except Item.DoesNotExist:
            pass

        return cleaned_data

    def save(self, commit=True):
        instance = super(ItemForm, self).save(False)  # inventory is missing

        instance.inventory = self.inventory

        if commit:
            instance.save()

        return instance


class ItemDeleteForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = []

    def delete(self):
        self.instance.delete()
