from django import forms

from pprint import pprint

class MergeDuplicatesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.helpers = kwargs.pop('helpers')

        super(MergeDuplicatesForm, self).__init__(*args, **kwargs)
        self.fields['helper_comment'] = forms.ModelChoiceField(
            queryset=self.helpers,
            required=False,
            widget=forms.RadioSelect()
        )
        self.fields['helper_email'] = forms.ModelChoiceField(
            queryset=self.helpers,
            widget=forms.RadioSelect()
        )
        self.fields['helper_name'] = forms.ModelChoiceField(
            queryset=self.helpers,
            widget=forms.RadioSelect()
        )
        self.fields['helper_phone'] = forms.ModelChoiceField(
            queryset=self.helpers,
            widget=forms.RadioSelect()
        )
        self.fields['helper_shirt'] = forms.ModelChoiceField(
            queryset=self.helpers,
            required=False,
            widget=forms.RadioSelect()
        )
        self.fields['helper_infection_instruction'] = forms.ModelChoiceField(
            queryset=self.helpers,
            required=False,
            widget=forms.RadioSelect()
        )
        self.fields['helper_vegetarian'] = forms.ModelChoiceField(
            queryset=self.helpers,
            required=False,
            widget=forms.RadioSelect()
        )
        self.fields['helper_barcode'] = forms.ModelChoiceField(
            queryset=self.helpers,
            required=False,
            widget=forms.RadioSelect()
        )
        self.fields['helper_shifts'] = forms.ModelMultipleChoiceField(
            queryset=self.helpers,
            widget=forms.CheckboxSelectMultiple(attrs={'id': 'helper'}),
            label='helpers_shifts')

        self.fields['helper_delete'] = forms.ModelMultipleChoiceField(
            queryset=self.helpers,
            widget=forms.CheckboxSelectMultiple(attrs={'id': 'helper'}),
            label='helpers_shifts')


    def merge(self):
        pprint(self.cleaned_data)
        ref = self.cleaned_data['helper_email']

        if self.cleaned_data['helper_comment']:
            ref.comment = self.cleaned_data['helper_comment'].comment

        # Merging email is not necessary - email is our reference!

        if self.cleaned_data['helper_name']:
            ref.firstname = self.cleaned_data['helper_name'].firstname
            ref.surname = self.cleaned_data['helper_name'].surname

        if self.cleaned_data['helper_phone']:
            ref.phone = self.cleaned_data['helper_phone'].phone

        if self.cleaned_data['helper_shirt']:
            ref.shirt = self.cleaned_data['helper_shirt'].shirt

        if self.cleaned_data['helper_infection_instruction']:
            ref.infection_instruction = self.cleaned_data['helper_infection_instruction'].infection_instruction

        if self.cleaned_data['helper_vegetarian']:
            ref.vegetarian = self.cleaned_data['helper_vegetarian'].vegetarian

        # Now merge all shifts that are marked for merging
        for helper in self.cleaned_data['helper_shifts']:
            if helper != ref:
                # merge shifts
                for shift in helper.shifts.all():
                    ref.shifts.add(shift)

                # merged coordinated jobs
                for job in helper.coordinated_jobs:
                    job.coordinators.add(ref)

                if ref.event.gifts:
                    ref.gifts.merge(helper.gifts)

        # TODO Do duplicate checking here!

        # Delete all duplicates that are marked for deleting - except ref!
        for helper in self.cleaned_data['helper_delete']:
            if helper != ref:
                helper.delete()

        return ref
