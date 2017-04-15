from django.forms import DateField, DateInput, DateTimeField, DateTimeInput


class DatePickerField(DateField):
    def __init__(self, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)

        self.widget = DateInput(attrs={
            'class': 'date',
            'addon_before': '<span class="glyphicon glyphicon-calendar">'
                            '</span>'
        })


class DateTimePickerField(DateTimeField):
    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)

        self.widget = DateTimeInput(attrs={
            'class': 'datetime',
            'addon_before': '<span class="glyphicon glyphicon-calendar">'
                            '</span>'
        })
