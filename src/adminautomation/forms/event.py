from django import forms
from django.utils.translation import gettext as _

from helfertool.forms import DatePicker

from ..models import EventArchiveAutomation


class EventArchiveStatusForm(forms.Form):
    months = forms.IntegerField(
        min_value=0,
        label=_("Months"),
    )


class EventArchiveExceptionForm(forms.ModelForm):
    class Meta:
        model = EventArchiveAutomation
        fields = ["exception_date"]
        widgets = {
            "exception_date": DatePicker,
        }
