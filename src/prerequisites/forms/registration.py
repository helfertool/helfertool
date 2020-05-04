from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.models import Helper, Shift
from ..models import Prerequisite

import logging
logger = logging.getLogger("helfertool")


class RegistrationPrerequisiteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.registerform = kwargs.pop('registerform')
        self.all_prerequisites = {}

        super(RegistrationPrerequisiteForm, self).__init__(*args, **kwargs)

        # create fields and store the prerequisites for later use
        for prerequisite in Prerequisite.objects.filter(event=self.event, visible=True).distinct():
            id_str = str(prerequisite.pk)

            self.fields[id_str] = forms.BooleanField(
                label=prerequisite.name,
                required=False
            )

            self.all_prerequisites[id_str] = prerequisite

    def clean(self):
        super(RegistrationPrerequisiteForm, self).clean()

        # get all needed prerequisites
        selected_shifts = [key for key, value in self.registerform.cleaned_data.items()
                           if ("shift_" in key) and (value is True)]
        self.required_prerequisites = {}

        # iterate over all (selected) shifts
        for shift in selected_shifts:
            cur_shift = Shift.objects.get(pk=self.registerform.shifts[shift])

            for prerequisite in cur_shift.job.prerequisites.filter(visible=True):
                self.required_prerequisites[str(prerequisite.pk)] = prerequisite

        # get all selected prerequisites
        selected_prerequisites = list(filter(lambda s: self.cleaned_data.get(s),
                                      self.all_prerequisites))

        # Match selected to needed prerequisites
        for p in self.required_prerequisites.values():
            if str(p.pk) not in selected_prerequisites:
                self.add_error(str(p.pk), _("You must fulfill all requirements for your shifts."))

    def save(self, helper):

        for p in self.required_prerequisites.values():
            p.set_helper(helper, True)

    def has_items(self):
        return bool(self.fields)
