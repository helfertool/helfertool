from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

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


def user_label_from_instance(obj):
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
        return user_label_from_instance(obj)


class UserSelectWidget(ModelSelect2MultipleWidget):
    """ Select2 widget for multiple users. """
    model = get_user_model()

    search_fields = [
        'username__icontains',
        'first_name__icontains',
        'last_name__icontains',
    ]

    def label_from_instance(self, obj):
        return user_label_from_instance(obj)


class ImageFileInput(forms.ClearableFileInput):
    """ ClearableFileInput that does not show the URL to the current file, but the image instead.

    If the image should be displayed, the parameter download_url must be set in the form
    (it is dynamic, so we cannot guess it here).
    """
    template_name = 'helfertool/forms/widgets/image_file_input.html'
    clear_checkbox_label = _("Delete image")

    download_url = None

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["download_url"] = self.download_url
        return context
