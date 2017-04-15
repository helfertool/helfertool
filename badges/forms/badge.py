from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import BadgeDesign, BadgeRole, Badge
from ..utils import is_image

from registration.models import Job


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        exclude = ['helper', 'barcode']

    def __init__(self, *args, **kwargs):
        super(BadgeForm, self).__init__(*args, **kwargs)

        # restrict queryset of primary_job
        jobs = Job.objects.filter(shift__helper=self.instance.helper).\
            distinct()
        coordinated_jobs = self.instance.helper.coordinated_jobs.distinct()

        self.fields['primary_job'].queryset = jobs | coordinated_jobs

        # restrict queryset of custom_role and custom_design
        badge_settings = self.instance.helper.event.badgesettings

        roles = BadgeRole.objects.filter(badge_settings=badge_settings)
        self.fields['custom_role'].queryset = roles

        designs = BadgeDesign.objects.filter(badge_settings=badge_settings)
        self.fields['custom_design'].queryset = designs

    def clean_photo(self):
        file = self.cleaned_data['photo']
        if file and not is_image(file):
            raise ValidationError(_("The file is not an image."))
        return file
