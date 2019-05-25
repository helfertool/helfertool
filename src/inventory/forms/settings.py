from django import forms

from django_select2.forms import Select2MultipleWidget

from ..models import InventorySettings


class InventorySettingsForm(forms.ModelForm):
    class Meta:
        model = InventorySettings
        exclude = ['event', ]
        widgets = {
            'available_inventory': Select2MultipleWidget,
        }
