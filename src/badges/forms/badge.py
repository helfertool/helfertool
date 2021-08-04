from django import forms
from django.urls import reverse

from helfertool.forms import ImageFileInput
from registration.models import Job

from ..models import BadgeDesign, BadgeRole, Badge


class BadgeForm(forms.ModelForm):
    """
    Edit a badge:
    * of a helper
    or
    * a special badge
    """
    class Meta:
        model = Badge
        exclude = ['event', 'helper', 'barcode']
        widgets = {
            'photo': ImageFileInput,
        }

    def __init__(self, *args, **kwargs):
        super(BadgeForm, self).__init__(*args, **kwargs)

        # check whether we edit a helper or a special badge
        if self.instance.helper:
            # restrict queryset of primary_job
            jobs = Job.objects.filter(shift__helper=self.instance.helper).distinct()
            coordinated_jobs = self.instance.helper.coordinated_jobs.distinct()

            self.fields['primary_job'].queryset = jobs | coordinated_jobs
        else:
            del self.fields['firstname']
            del self.fields['surname']
            del self.fields['primary_job']
            del self.fields['printed']

        # restrict queryset of custom_role and custom_design
        badge_settings = self.instance.event.badgesettings

        roles = BadgeRole.objects.filter(badge_settings=badge_settings)
        self.fields['custom_role'].queryset = roles

        designs = BadgeDesign.objects.filter(badge_settings=badge_settings)
        self.fields['custom_design'].queryset = designs

        # set download_url parameters for widgets
        if self.instance.helper:
            # for normal badge
            url_args = [self.instance.event.url_name, self.instance.helper.pk]
            self.fields["photo"].widget.download_url = reverse("badges:get_badge_photo", args=url_args)
        else:
            # for special badges
            url_args = [self.instance.event.url_name, self.instance.pk]
            self.fields["photo"].widget.download_url = reverse("badges:get_specialbadges_photo", args=url_args)
