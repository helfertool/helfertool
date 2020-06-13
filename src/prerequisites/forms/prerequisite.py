from django import forms
from django.conf import settings
from ckeditor.widgets import CKEditorWidget

from ..models import Prerequisite


class PrerequisiteForm(forms.ModelForm):
    """
    Form for new prerequisite creation
    """
    class Meta:
        model = Prerequisite
        exclude = ['name', 'description', 'event', ]

        widgets = {}

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        for lang, name in settings.LANGUAGES:
            widgets["description_{}".format(lang)] = CKEditorWidget()

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(PrerequisiteForm, self).__init__(*args, **kwargs)

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
