from django import forms
from django.conf import settings

from ckeditor.widgets import CKEditorWidget

from ..models import Job
from badges.models import BadgeRole

from .fields import UserSelectField


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ['name', 'description', 'event', 'coordinators',
                   'badge_defaults', ]
        field_classes = {
            'admins': UserSelectField,
        }
        widgets = {}

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        for lang, name in settings.LANGUAGES:
            widgets["description_{}".format(lang)] = CKEditorWidget()

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(JobForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(JobForm, self).save(False)  # event is missing

        # add event
        instance.event = self.event

        if commit:
            instance.save()

        self.save_m2m()  # save m2m, otherwise job_admins is lost

        return instance


class JobDeleteForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = []

    def delete(self):
        self.instance.delete()
