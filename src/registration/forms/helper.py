from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.functions import Greatest
from django.utils.translation import ugettext_lazy as _

from ..models import Helper, Shift, Job
from ..permissions import has_access, ACCESS_HELPER_VIEW, ACCESS_JOB_EDIT_HELPERS
from badges.models import Badge


class HelperForm(forms.ModelForm):
    class Meta:
        model = Helper
        exclude = ['event', 'shifts', 'privacy_statement', 'mail_failed', 'internal_comment', 'prerequisites']

    def __init__(self, *args, **kwargs):
        self.related_event = kwargs.pop('event')
        self.job = kwargs.pop('job', None)
        self.public = kwargs.pop('public', False)

        super(HelperForm, self).__init__(*args, **kwargs)

        # remove field for phone number
        if not self.related_event.ask_phone:
            self.fields.pop('phone')

        # remove field for shirt?
        if not self.related_event.ask_shirt:
            self.fields.pop('shirt')
        else:
            self.fields['shirt'].choices = \
                self.related_event.get_shirt_choices(True)

        # remove field for vegetarian food?
        if not self.related_event.ask_vegetarian:
            self.fields.pop('vegetarian')

        # remove field for instruction for food handling
        if not self.instance.needs_infection_instruction and \
                not (self.job and self.job.infection_instruction):
            self.fields.pop('infection_instruction')

        # remove field for mail validation if
        # 1) form is used to add new coordinator to a job
        # 2) is public
        if self.job or self.public:
            self.fields.pop('validated')

        # store old mail address for comparison
        self.old_email = self.instance.email

    def save(self, commit=True):
        instance = super(HelperForm, self).save(False)

        instance.event = self.related_event

        if self.related_event.mail_validation:
            # new coordinator for job needs to validate mail address
            if self.job:
                instance.validated = False

            # invalidate email if it was changed. sending out the new mail is done in the view
            if self.old_email != instance.email:
                instance.validated = False
                instance.mail_failed = None

        if commit:
            instance.save()

        if self.job:
            self.job.coordinators.add(self.instance)

        return instance

    @property
    def email_has_changed(self):
        return self.old_email != self.instance.email


class HelperAddShiftForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.helper = kwargs.pop('helper')
        self.user = kwargs.pop('user')

        super(HelperAddShiftForm, self).__init__(*args, **kwargs)

        event = self.helper.event

        # field that contains all shifts if
        #  - user is admin for shift/job
        #  - helper is not already in this shift

        # all administered shifts
        administered_jobs = [job for job in event.job_set.all()
                             if has_access(self.user, job, ACCESS_JOB_EDIT_HELPERS)]
        shifts = Shift.objects.filter(job__event=event,
                                      job__in=administered_jobs)

        # exclude already taken shifts
        shifts = shifts.exclude(id__in=self.helper.shifts.all())

        # add field
        self.fields['shifts'] = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=shifts, required=True)

    def clean(self):
        super(HelperAddShiftForm, self).clean()

        if 'shifts' not in self.cleaned_data:
            raise ValidationError(_("No shifts selected"))

        for shift in self.cleaned_data.get('shifts'):
            if shift.is_full():
                raise ValidationError(_("This shift if already full: {}".format(shift)))

    def save(self):
        for shift in self.cleaned_data.get('shifts'):
            self.helper.shifts.add(shift)
        self.helper.save()


class HelperAddCoordinatorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.helper = kwargs.pop('helper')
        self.user = kwargs.pop('user')

        super(HelperAddCoordinatorForm, self).__init__(*args, **kwargs)

        event = self.helper.event

        # field that contains all jobs if
        #  - user is admin for job
        #  - helper is not already coordinator for this job

        # all administered jobs
        coordinated_jobs = self.helper.coordinated_jobs
        jobs = [job.pk for job in event.job_set.all()
                if has_access(self.user, job, ACCESS_JOB_EDIT_HELPERS) and job not in coordinated_jobs]

        # we need a queryset
        jobs = Job.objects.filter(pk__in=jobs)

        # add field
        self.fields['jobs'] = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=jobs, required=True)

    def save(self, commit=True):
        for job in self.cleaned_data.get('jobs'):
            job.coordinators.add(self.helper)
            job.save()


class HelperDeleteForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['shifts', ]
        widgets = {
            'shifts': forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        self.shift = kwargs.pop('shift')
        self.user = kwargs.pop('user')
        self.show_all_shifts = kwargs.pop('show_all_shifts')

        super(HelperDeleteForm, self).__init__(*args, **kwargs)

        # show only the one specified shift or shifts, where the helper is
        # registered
        if self.show_all_shifts:
            self.fields['shifts'].queryset = self.instance.shifts
        else:
            self.fields['shifts'].queryset = Shift.objects.filter(
                pk=self.shift.pk)  # we need a queryset, not a Shift object

        self.fields['shifts'].required = False  # show customized error message in clean

    def clean(self):
        super(HelperDeleteForm, self).clean()

        # check if shifts selected
        if len(self.get_deleted_shifts()) == 0:
            raise ValidationError(_("No shift selected"))

        # check if user is admin for all shifts that will be deleted
        for shift in self.get_deleted_shifts():
            if not has_access(self.user, shift.job, ACCESS_JOB_EDIT_HELPERS):
                raise ValidationError(_("You are not allowed to delete a "
                                        "helper from the job \"%(jobname)s\"")
                                      % {'jobname': shift.job.name})

    def get_deleted_shifts(self):
        return self.cleaned_data.get('shifts')

    def delete(self):
        # delete all selected shifts
        for shift in self.cleaned_data.get('shifts'):
            self.instance.shifts.remove(shift)


class HelperDeleteCoordinatorForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = []

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job')

        super(HelperDeleteCoordinatorForm, self).__init__(*args, **kwargs)

    def delete(self):
        self.job.coordinators.remove(self.instance)


class HelperSearchForm(forms.Form):
    pattern = forms.CharField(
        min_length=2,
        max_length=100,
        label=_("Search term"),
        widget=forms.TextInput(attrs={'autofocus': ''}),
    )

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.user = kwargs.pop('user')

        super(HelperSearchForm, self).__init__(*args, **kwargs)

    def check_barcode(self):
        if not self.event.badges:
            return None

        p = self.cleaned_data.get('pattern')

        try:
            barcode = int(p)
        except ValueError:
            return None

        try:
            badge = Badge.objects.get(helper__event=self.event,
                                      barcode=barcode)
        except Badge.DoesNotExist:
            return None

        if has_access(self.user, badge.helper, ACCESS_HELPER_VIEW):
            return badge.helper

        return None

    def get(self):
        p = self.cleaned_data.get('pattern')

        if settings.SEARCH_SIMILARITY_DISABLED:
            # traditional direct-matching
            data = self.event.helper_set.filter(Q(firstname__icontains=p) |
                                                Q(surname__icontains=p) |
                                                Q(email__icontains=p) |
                                                Q(phone__icontains=p))
        else:
            # proper databases support -> fuzzy-matching
            data = self.event.helper_set.annotate(
                similarity_fn=TrigramSimilarity('firstname', p),
                similarity_sn=TrigramSimilarity('surname', p),
            ).annotate(
                similarity=Greatest('similarity_fn', 'similarity_sn'),
            ).filter(
                Q(similarity__gte=settings.SEARCH_SIMILARITY) |
                Q(email__icontains=p) |
                Q(phone__icontains=p)
            ).order_by('-similarity')

        data = filter(lambda h: has_access(self.user, h, ACCESS_HELPER_VIEW), data)

        return list(data)  # directly evaluate filter here


class HelperResendMailForm(forms.Form):
    pass


class HelperInternalCommentForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['internal_comment', ]

    def __init__(self, *args, **kwargs):
        super(HelperInternalCommentForm, self).__init__(*args, **kwargs)

        self.fields['internal_comment'].widget.attrs['rows'] = 3

    def clean(self):
        cleaned_data = super(HelperInternalCommentForm, self).clean()

        self.cleaned_data['internal_comment'] = self.cleaned_data['internal_comment'].strip()

        return cleaned_data
