from django.forms import ModelMultipleChoiceField, SelectMultiple

class DualListField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(DualListField, self).__init__(*args, **kwargs)

        self.widget =  SelectMultiple(attrs={'class': 'duallistbox'})
