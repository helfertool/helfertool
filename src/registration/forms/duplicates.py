from django import forms
from django.db import transaction

from ..models import Duplicate, HelperShift


class MergeDuplicatesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._helpers = kwargs.pop('helpers')

        super(MergeDuplicatesForm, self).__init__(*args, **kwargs)

        self.fields['helpers'] = forms.ModelChoiceField(
            queryset=self._helpers,
            widget=forms.RadioSelect(attrs={'id': 'helper'}),
            empty_label=None,
            required=True,
            label='')

    @transaction.atomic
    def merge(self):
        """
        Merge the helpers and keep the data selected in the form.
        """
        remaining_helper = self.cleaned_data['helpers']
        oldest_timestamp = remaining_helper.timestamp

        # check it again inside atomic code block. we do error handling here and not in validate
        # to make sure that no change happends after the validation and before the merge
        if not self.check_merge_possible():
            raise ValueError("Cannot merge helpers with same shifts")

        # and then to the merge
        for helper in self._helpers:
            if helper != remaining_helper:
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
                Duplicate.objects.create(deleted=helper.id,
                                         existing=remaining_helper)

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

    def check_merge_possible(self):
        """
        Check if the merge is possible.

        It is not possible when multiple helpers have the same shift. If we would merge those helpers,
        we would "loose" allocated seats and this is probably not intended.
        """
        shifts = []
        for helper in self._helpers:
            for shift in helper.shifts.all():
                if shift in shifts:
                    return False
                else:
                    shifts.append(shift)
        return True
