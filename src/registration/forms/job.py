from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import formats
from django.utils.translation import gettext_lazy as _

from helfertool.forms import DatePicker, SingleUserSelectWidget
from prerequisites.forms import PrerequisiteSelectWidget
from prerequisites.models import Prerequisite

from ..models import Job, JobAdminRoles

from ckeditor.widgets import CKEditorWidget
from datetime import datetime


class JobForm(forms.ModelForm):
    class Meta:
        model = Job

        # note: change also below in JobDuplicateForm
        exclude = [
            "name",
            "description",
            "important_notes",
            "event",
            "coordinators",
            "badge_defaults",
            "archived_number_coordinators",
            "order",
            "job_admins",
        ]
        widgets = {
            "prerequisites": PrerequisiteSelectWidget,
        }

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        for lang, name in settings.LANGUAGES:
            widgets["description_{}".format(lang)] = CKEditorWidget()
            widgets["important_notes_{}".format(lang)] = CKEditorWidget()

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop("event")

        super(JobForm, self).__init__(*args, **kwargs)

        # remove or configure prerequisites field
        if not self.event.prerequisites:
            self.fields.pop("prerequisites")
        else:
            self.fields["prerequisites"].queryset = Prerequisite.objects.filter(event=self.event)

        # set better label for description fields
        for lang, name in settings.LANGUAGES:
            self.fields["description_{}".format(lang)].label = _("Description (%(lang)s)") % {"lang": name}
            self.fields["important_notes_{}".format(lang)].label = _("Important notes (%(lang)s)") % {"lang": name}

    def save(self, commit=True):
        instance = super(JobForm, self).save(False)  # event is missing

        # add event
        instance.event = self.event

        if commit:
            instance.save()

        self.save_m2m()  # save m2m, otherwise prerequisites are lost

        return instance


class JobAdminRolesForm(forms.ModelForm):
    class Meta:
        model = JobAdminRoles
        fields = [
            "roles",
        ]


class JobAdminRolesAddForm(forms.ModelForm):
    class Meta:
        model = JobAdminRoles
        fields = [
            "user",
            "roles",
        ]
        widgets = {
            "user": SingleUserSelectWidget,
        }

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop("job")

        super(JobAdminRolesAddForm, self).__init__(*args, **kwargs)

        # we want to be able to submit an empty form as it is part of a page with multiple forms
        # if no user is set, the form is still valid and the save does not change anything
        self.fields["user"].required = False

    def save(self, commit=True):
        # if no user given, just skip it
        if self.cleaned_data["user"]:
            instance = super(JobAdminRolesAddForm, self).save(False)
            instance.job = self.job
            if commit:
                instance.save()
            return instance

    def clean_user(self):
        user = self.cleaned_data["user"]

        # user already has admin privileges for this job -> invalid
        if user and JobAdminRoles.objects.filter(job=self.job, user=user).exists():
            raise ValidationError(_("User already has permissions for this job assigned"))

        return user


class JobDeleteForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = []

    def delete(self):
        self.instance.delete()


class JobDuplicateForm(JobForm):
    def __init__(self, *args, **kwargs):
        self.other_job = kwargs.pop("other_job")
        kwargs["event"] = self.other_job.event
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
        self.job = kwargs.pop("job")
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

        self.fields["old_date"].choices = old_date_choices

    def save(self):
        cleaned_data = super().clean()

        old_date = datetime.strptime(cleaned_data.get("old_date"), "%Y-%m-%d").date()
        new_date = cleaned_data.get("new_date")

        shifts = self.job.shift_set.filter(begin__date=old_date)
        for shift in shifts:
            shift.duplicate(new_date=new_date)

        return shifts


class JobSortForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._event = kwargs.pop("event")

        super().__init__(*args, **kwargs)

        counter = self._event.job_set.count()
        for job in self._event.job_set.all():
            field_id = "order_job_%s" % job.pk

            self.fields[field_id] = forms.IntegerField(min_value=0, initial=counter)
            self.fields[field_id].widget = forms.HiddenInput()

            counter -= 1

    def save(self):
        cleaned_data = super().clean()

        for job in self._event.job_set.all():
            field_id = "order_job_%s" % job.pk
            job.order = cleaned_data.get(field_id)
            job.save()
