from django import forms
from django.contrib.auth import get_user_model

from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


class DatePicker(forms.DateInput):
    """ Date picker (browser native) """
    input_type = "date"

    def __init__(self):
        super(DatePicker, self).__init__(format='%Y-%m-%d')


class DateTimePicker(forms.SplitDateTimeWidget):
    """ Date and time picker (separate boxes, browser native) """
    def __init__(self):
        super(DateTimePicker, self).__init__(
            date_format='%Y-%m-%d',
            date_attrs={'type': 'date'},
            time_format='%H:%M',
            time_attrs={'type': 'time', 'class': 'mt-1'},
        )


def _user_label_from_instance(self, obj):
    if obj.first_name and obj.last_name:
        return "{} ({})".format(obj.get_full_name(), obj.get_username())
    return obj.get_username()


class SingleUserSelectWidget(ModelSelect2Widget):
    """ Select2 widget for single user. """
    model = get_user_model()

    search_fields = [
        'username__icontains',
        'first_name__icontains',
        'last_name__icontains',
    ]

    def label_from_instance(self, obj):
        return _user_label_from_instance(self, obj)


class UserSelectWidget(ModelSelect2MultipleWidget):
    """ Select2 widget for multiple users. """
    model = get_user_model()

    search_fields = [
        'username__icontains',
        'first_name__icontains',
        'last_name__icontains',
    ]

    def label_from_instance(self, obj):
        return _user_label_from_instance(self, obj)
