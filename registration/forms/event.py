from django import forms
from django.conf import settings

from ckeditor.widgets import CKEditorWidget

from ..models import Event

from .fields import UserSelectField


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['text', 'imprint', 'registered', 'badge_settings',
                   'archived', ]
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

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        if self.instance.archived:
            for field_id in self.fields:
                if field_id != "admins":
                    self.fields[field_id].disabled = True


class EventDeleteForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = []

    def delete(self):
        self.instance.delete()

class EventArchiveForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = []

    def archive(self):
        self.instance.archived = True
        self.instance.active = False
        self.instance.save()

        for job in self.instance.job_set.all():
            # delete coordinators
            job.archived_number_coordinators = job.coordinators.count()
            job.save()

            # trigger post_remove signal
            for c in job.coordinators.all():
                job.coordinators.remove(c)

            # now the shifts
            for shift in job.shift_set.all():
                shift.archived_number = shift.helper_set.count()
                shift.save()

                # trigger post_remove signal
                for h in shift.helper_set.all():
                    h.shifts.remove(shift)
