from django import forms

from ..models import Link, Shift


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ['event', 'creator']
        widgets = {
            'shifts': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.creator = kwargs.pop('creator')

        super(LinkForm, self).__init__(*args, **kwargs)

        # only show shifts for this event
        self.fields['shifts'].queryset = Shift.objects.filter(
            job__event=self.event)

    def save(self, commit=True):
        instance = super(LinkForm, self).save(False)

        # add event and creator
        instance.event = self.event
        # if instance.creator is None:
        instance.creator = self.creator  # FIXME

        if commit:
            instance.save()

        self.save_m2m()

        return instance


class LinkDeleteForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = []

    def delete(self):
        self.instance.delete()
