from django import forms

class DatePicker(forms.DateInput):
    input_type = 'date'

    def __init__(self):
        super(DatePicker, self).__init__(format='%Y-%m-%d')

class DateTimePicker(forms.SplitDateTimeWidget):
    def __init__(self):
        # TODO: use this for django >= 2.0 and delete code below
        #super(DateTimePicker, self).__init__(
        #    date_format='%Y-%m-%d',
        #    date_attrs={'type': 'date'},
        #    time_format='%H:%M',
        #    time_attrs={'type': 'time'},
        #)

        widgets = (
            forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'},
            ),
            forms.TimeInput(
                format='%H:%M',
                attrs={'type': 'time'},
            ),
        )
        super(forms.SplitDateTimeWidget, self).__init__(widgets, None)
