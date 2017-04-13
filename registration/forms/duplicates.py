from django import forms


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

    def merge(self):
        remaining_helper = self.cleaned_data['helpers']

        for helper in self._helpers:
            if helper != remaining_helper:
                # merge shifts
                for shift in helper.shifts.all():
                    remaining_helper.shifts.add(shift)

                # merged coordinated jobs
                for job in helper.coordinated_jobs:
                    job.coordinators.add(remaining_helper)

                if remaining_helper.event.gifts:
                    remaining_helper.gifts.merge(helper.gifts)

                helper.delete()

        return remaining_helper
