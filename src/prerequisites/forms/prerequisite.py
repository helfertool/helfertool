from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ..models import Prerequisite


class PrerequisiteForm(forms.ModelForm):
    """
    Form for new prerequisite creation
    """

    class Meta:
        model = Prerequisite
        exclude = [
            "name",
            "description",
            "event",
        ]

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop("event")

        super(PrerequisiteForm, self).__init__(*args, **kwargs)

        # set better label for description fields
        for lang, name in settings.LANGUAGES:
            self.fields["description_{}".format(lang)].label = _("Description (%(lang)s)") % {"lang": name}

    def save(self, commit=True):
        instance = super(PrerequisiteForm, self).save(False)  # event is missing

        # add event
        instance.event = self.event

        if commit:
            instance.save()

        return instance


class PrerequisiteDeleteForm(forms.ModelForm):
    """
    Prerequisite deletion
    """

    class Meta:
        model = Prerequisite
        fields = []

    def delete(self):
        self.instance.delete()
