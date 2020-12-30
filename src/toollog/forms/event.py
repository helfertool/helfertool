from django import forms

from ..models import LogEntry
from toolsettings.forms import SingleUserSelectWidget
from registration.forms import SingleHelperSelectWidget


class EventAuditLogFilter(forms.ModelForm):
    class Meta:
        model = LogEntry
        fields = ("user", "helper", "message",)
        widgets = {
            'user': SingleUserSelectWidget,
            'helper': SingleHelperSelectWidget,
        }

    def __init__(self, *args, **kwargs):
        self._event = kwargs.pop("event")
        super(EventAuditLogFilter, self).__init__(*args, **kwargs)

        # restrict helpers to this event
        self.fields['helper'].queryset = self._event.helper_set

        # message is required in model, but not for search
        self.fields["message"].required = False

    def save(self, commit=True):
        raise NotImplementedError("This model form is only for filtering!")
