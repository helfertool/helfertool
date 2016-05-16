from django import forms
from django.conf import settings

from ckeditor.widgets import CKEditorWidget

from ..models import Event

from .fields import UserSelectField


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['text', 'imprint', 'registered', 'badge_settings']
        field_classes = {
            'admins': UserSelectField,
        }
        widgets = {
            'date': forms.DateInput(attrs={'class': 'date'}),
            'text': CKEditorWidget(),
        }

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        for w in ('text', 'imprint', 'registered'):
            for lang, name in settings.LANGUAGES:
                widgets["{}_{}".format(w, lang)] = CKEditorWidget()


class EventDeleteForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = []

    def delete(self):
        self.instance.delete()
