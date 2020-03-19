from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from ckeditor.widgets import CKEditorWidget

from .models import Prerequisite, FulfilledPrerequisite


class PrerequisiteForm(forms.ModelForm):
    """
    form for new prerequisite creation
    """
    class Meta:
        model = Prerequisite
        exclude = ['long_name', 'description', 'event']

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

        self.save_m2m()

        return instance

    def clean(self):

        cleaned_data = self.cleaned_data

        name = cleaned_data.get("name")
        event = self.event

        if Prerequisite.objects.filter(event=event, name=name).count() > 0:
            raise forms.ValidationError("Prerequisite already exists.")

        # Always return the full collection of cleaned data.
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


class HelperPrerequisiteForm(forms.Form):
    """
    Shows all needed prerequisites for a helper
    """

    def __init__(self, *args, **kwargs):
        self.helper = kwargs.pop('helper')

        super(HelperPrerequisiteForm, self).__init__(*args, **kwargs)

        # Get all unique prerequisites that this helper has
        all_helper_prerequisites = Prerequisite.objects.all()\
            .filter(job__shift__helper=self.helper)\
            .distinct()

        for prereqisite in all_helper_prerequisites:
            id_str = "prerequisite_{}".format(prereqisite.pk)

            # If helper-prerequisite relation exists, get its status
            try:
                fulfilled = prereqisite.fulfilledprerequisite_set.get(helper=self.helper)
            except FulfilledPrerequisite.DoesNotExist:
                fulfilled = None

            self.fields[id_str] = forms.BooleanField(
                label=prereqisite.name,
                required=False,
                initial=fulfilled is not None and fulfilled.has_prerequisite
            )

    def save(self):
        # Get all unique prerequisites that this helper has
        all_helper_prerequisites = Prerequisite.objects.all() \
            .filter(job__shift__helper=self.helper) \
            .distinct()

        for prereqisite in all_helper_prerequisites:
            id_str = "prerequisite_{}".format(prereqisite.pk)

            # Check if helper-prerequisite relation exists
            fulfilled = self.cleaned_data.get(id_str)
            FulfilledPrerequisite.objects.update_or_create(helper=self.helper, prerequisite=prereqisite,
                                                           defaults={'has_prerequisite': fulfilled})

    def has_items(self):
        return bool(self.fields)