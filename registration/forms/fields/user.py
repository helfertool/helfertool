from django.forms import ModelMultipleChoiceField, SelectMultiple

class UserSelectField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(UserSelectField, self).__init__(*args, **kwargs)

        self.widget =  SelectMultiple(attrs={'class': 'duallistbox'})
    def label_from_instance(self, obj):
        if obj.first_name and obj.last_name:
            return obj.get_full_name()
        return obj.get_username()
