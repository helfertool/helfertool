from django import forms
from django.db import transaction
from django.utils.translation import ugettext as _

from ..models import Duplicate, HelperShift


class MergeDuplicatesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.helpers = kwargs.pop("helpers")

        super(MergeDuplicatesForm, self).__init__(*args, **kwargs)

        self.fields["helpers_ignore"] = forms.ModelMultipleChoiceField(
            queryset=self.helpers,
            widget=forms.CheckboxSelectMultiple(attrs={"id": "helper_ignore"}),
            required=False,
            label="",
        )

        self.fields["helpers_selection"] = forms.ModelChoiceField(
            queryset=self.helpers,
            widget=forms.RadioSelect(attrs={"id": "helper_selection"}),
            empty_label=None,
            required=True,
            label="",
        )

    def clean(self):
        cleaned_data = super().clean()
        remaining_helper = cleaned_data["helpers_selection"]
        ignore_helpers = cleaned_data["helpers_ignore"]

        # remaining helpers must not be ignored (this makes no sense)
        if remaining_helper in ignore_helpers:
            raise forms.ValidationError(_("The remaining helper must not be ignored."))

        # check for overlapping shifts
        if not self.check_merge_possible(ignore_helpers):
            raise forms.ValidationError(_("Cannot merge helpers which have the same shift."))

    @transaction.atomic
    def merge(self):
        """
        Merge the helpers and keep the data selected in the form.
        """
        remaining_helper = self.cleaned_data["helpers_selection"]
        ignore_helpers = self.cleaned_data["helpers_ignore"]
        oldest_timestamp = remaining_helper.timestamp

        # we check this again inside the atomic code block to ensure that no change happends after the
        # validation and before the merge (= no new shifts were added)
        if not self.check_merge_possible(ignore_helpers):
            raise ValueError("Cannot merge helpers with same shifts")

        # and then to the merge
        for helper in self.helpers:
            if helper == remaining_helper or helper in ignore_helpers:
                continue
            # merge shifts
            for helpershift in HelperShift.objects.filter(helper=helper):
                helpershift.helper = remaining_helper
                helpershift.save()

            # merged coordinated jobs
            for job in helper.coordinated_jobs:
                job.coordinators.add(remaining_helper)

            # merge gifts
            if remaining_helper.event.gifts:
                remaining_helper.gifts.merge(helper.gifts)

            # then create the duplicate entry so that old links in mails still work
            Duplicate.objects.create(deleted=helper.id, existing=remaining_helper)

            # the overall timestamp of the helper should be the oldest one
            # (there are multiple timestamps saved: one per helper and one per shift)
            if helper.timestamp < oldest_timestamp:
                oldest_timestamp = helper.timestamp

            # and delete the old helper
            helper.delete()

        # update timestamp
        remaining_helper.timestamp = oldest_timestamp
        remaining_helper.save()

        return remaining_helper

    def check_merge_possible(self, ignore_helpers=None):
        """
        Check if the merge is possible.

        It is not possible when multiple helpers have the same shift. If we would merge those helpers,
        we would "loose" allocated seats and this is probably not intended.
        """
        shifts = []
        for helper in self.helpers:
            # if we have ignored_helpers, check that
            if ignore_helpers and helper in ignore_helpers:
                continue

            # compare all shifts
            for shift in helper.shifts.all():
                if shift in shifts:
                    return False
                else:
                    shifts.append(shift)
        return True
