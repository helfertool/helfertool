from django_select2.forms import ModelSelect2MultipleWidget

from ..models import Prerequisite


class PrerequisiteSelectWidget(ModelSelect2MultipleWidget):
    model = Prerequisite

    search_fields = [
        'name__icontains',
    ]

    def label_from_instance(self, obj):
        return obj.name
