from django import forms

from ..models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['text', 'imprint', 'registered', 'badge_settings']
        widgets = {
            'admins': forms.SelectMultiple(attrs={'class': 'duallistbox'}),
            'date': forms.DateInput(attrs={'class': 'date'}),
        }


class EventDeleteForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = []

    def delete(self):
        self.instance.delete()
