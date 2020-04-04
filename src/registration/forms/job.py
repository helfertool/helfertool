from django import forms
from django.conf import settings
from django.utils import formats
from django.utils.translation import ugettext_lazy as _

from ckeditor.widgets import CKEditorWidget
from datetime import datetime

from toolsettings.forms import UserSelectWidget
from prerequisites.forms import PrerequisiteSelectWidget
from prerequisites.models import Prerequisite

from .fields import DatePicker
from ..models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job

        # note: change also below in JobDuplicateForm
        exclude = ['name', 'description', 'event', 'coordinators',
                   'badge_defaults', 'archived_number_coordinators',
                   'order', ]
        widgets = {
            'job_admins': UserSelectWidget,
            'prerequisites': PrerequisiteSelectWidget,
        }

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        for lang, name in settings.LANGUAGES:
            widgets["description_{}".format(lang)] = CKEditorWidget()

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(JobForm, self).__init__(*args, **kwargs)

        if not self.event.prerequisites:
            self.fields.pop('prerequisites')
        else:
            self.fields['prerequisites'].queryset = Prerequisite.objects.filter(event=self.event)

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


class JobDuplicateForm(JobForm):
    def __init__(self, *args, **kwargs):
        self.other_job = kwargs.pop('other_job')
        kwargs['event'] = self.other_job.event
        super(JobDuplicateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        super(JobDuplicateForm, self).save(commit=True)  # we have to save

        for shift in self.other_job.shift_set.all():
            shift.duplicate(new_job=self.instance)

        return self.instance


class JobDuplicateDayForm(forms.Form):
    old_date = forms.ChoiceField(
        label=_("Date to copy from"),
    )

    new_date = forms.DateField(
        label=_("New date"),
        widget=DatePicker,
    )

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job')
        super(JobDuplicateDayForm, self).__init__(*args, **kwargs)

        # get a list of all days where a shifts begins
        day_with_shifts = []
        for shift in self.job.shift_set.all():
            day = shift.date()
            if day not in day_with_shifts:
                day_with_shifts.append(day)

        # and set choices for field
        old_date_choices = []
        for day in sorted(day_with_shifts):
            day_str = str(day)
            day_localized = formats.date_format(day, "SHORT_DATE_FORMAT")
            old_date_choices.append((day_str, day_localized))

        self.fields['old_date'].choices = old_date_choices

    def save(self):
        cleaned_data = super().clean()

        old_date = datetime.strptime(cleaned_data.get("old_date"), "%Y-%m-%d").date()
        new_date = cleaned_data.get('new_date')

        shifts = self.job.shift_set.filter(begin__date=old_date)
        for shift in shifts:
            shift.duplicate(new_date=new_date)

        return shifts


class JobSortForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._event = kwargs.pop('event')

        super().__init__(*args, **kwargs)

        counter = self._event.job_set.count()
        for job in self._event.job_set.all():
            field_id = 'order_job_%s' % job.pk

            self.fields[field_id] = forms.IntegerField(min_value=0, initial=counter)
            self.fields[field_id].widget = forms.HiddenInput()

            counter -= 1

    def save(self):
        cleaned_data = super().clean()

        for job in self._event.job_set.all():
            field_id = 'order_job_%s' % job.pk
            job.order = cleaned_data.get(field_id)
            job.save()
