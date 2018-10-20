from django_select2.forms import Select2MultipleWidget


class UserSelectWidget(Select2MultipleWidget):
    def label_from_instance(self, obj):
        # FIXME
        if obj.first_name and obj.last_name:
            return "{} ({})".format(obj.get_full_name(), obj.get_username())
        return obj.get_username()
