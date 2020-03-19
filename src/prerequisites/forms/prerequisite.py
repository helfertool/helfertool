from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from ckeditor.widgets import CKEditorWidget

from ..models import Prerequisite, FulfilledPrerequisite


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

    def clean(self):
        cleaned_data = super(PrerequisiteForm, self).clean()

        # when object is newly created, check that name is unique
        if self.instance.pk is None and \
            Prerequisite.objects.filter(event=self.event, name=cleaned_data["name"]).exists():
            raise forms.ValidationError(_("Prerequisite already exists."))

        return cleaned_data


class PrerequisiteDeleteForm(forms.ModelForm):
    """
    Prerequisite deletion
    """
    class Meta:
        model = Prerequisite
        fields = []

    def delete(self):
        self.instance.delete()
