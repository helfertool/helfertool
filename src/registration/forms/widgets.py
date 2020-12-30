from django_select2.forms import ModelSelect2Widget

from ..models import Helper


class SingleHelperSelectWidget(ModelSelect2Widget):
    model = Helper

    search_fields = [
        'firstname__icontains',
        'surname__icontains',
    ]

    def label_from_instance(self, obj):
        return obj.full_name
