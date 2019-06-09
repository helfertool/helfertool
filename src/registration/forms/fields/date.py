from django import forms
from django.utils.translation import ugettext_lazy as _


class DatePicker(forms.DateInput):
    input_type = 'date'

    def __init__(self):
        super(DatePicker, self).__init__(format='%Y-%m-%d')


class DateTimePicker(forms.SplitDateTimeWidget):
    def __init__(self):
        super(DateTimePicker, self).__init__(
            date_format='%Y-%m-%d',
            date_attrs={'type': 'date'},
            time_format='%H:%M',
            time_attrs={'type': 'time'},
        )
