from django.contrib.auth.models import User
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


def _label_from_instance(self, obj):
    if obj.first_name and obj.last_name:
        return "{} ({})".format(obj.get_full_name(), obj.get_username())
    return obj.get_username()


class SingleUserSelectWidget(ModelSelect2Widget):
    model = User

    search_fields = [
        'username__icontains',
        'first_name__icontains',
        'last_name__icontains',
    ]

    def label_from_instance(self, obj):
        return _label_from_instance(self, obj)


class UserSelectWidget(ModelSelect2MultipleWidget):
    model = User

    search_fields = [
        'username__icontains',
        'first_name__icontains',
        'last_name__icontains',
    ]

    def label_from_instance(self, obj):
        return _label_from_instance(self, obj)
