from django import forms

from ..models import ContactTracingData


class CoronaCleanupForm(forms.Form):
    def cleanup(self, event):
        ContactTracingData.objects.filter(event=event).delete()
