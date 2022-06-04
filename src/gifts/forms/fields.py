from django.forms import ChoiceField, RadioSelect
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import lazy

from django_icons import icon


def choice(icon_name, classes, text):
    return mark_safe(
        format_lazy('<span class="{classes}"> {icon} {text}</span>', icon=icon(icon_name), classes=classes, text=text)
    )


choice_lazy = lazy(choice)


class PresenceField(ChoiceField):
    """
    This field gets a HelperShift as input and returns the presence status as True/False/None:

    * True: the helper was present
    * False: the helper was absent
    * None: Auto/Unkown was selected
    """

    PRESENCE_AUTO = "auto"
    PRESENCE_UNKNOWN = "unknown"
    PRESENCE_PRESENT = "present"
    PRESENCE_ABSENT = "absent"

    PRESENCE_CHOICES_AUTO = [
        (PRESENCE_AUTO, choice_lazy("clock", "text-info", _("Auto"))),
    ]

    PRESENCE_CHOICES_UNKNOWN = [
        (PRESENCE_UNKNOWN, choice_lazy("question", "text-info", _("Unknown"))),
    ]

    PRESENCE_CHOICES = [
        (PRESENCE_PRESENT, choice_lazy("check", "text-success", _("Present"))),
        (PRESENCE_ABSENT, choice_lazy("times", "text-danger", _("Absent"))),
    ]

    def __init__(self, *args, **kwargs):
        automatic_presence = kwargs.pop("automatic_presence")
        helpershift = kwargs.pop("helpershift")
        disabled = kwargs.pop("disabled", False)

        # depending on the automatic presence setting, add "auto" or "unknown"
        if automatic_presence:
            choices = self.PRESENCE_CHOICES_AUTO + self.PRESENCE_CHOICES
        else:
            choices = self.PRESENCE_CHOICES_UNKNOWN + self.PRESENCE_CHOICES

        # initial value
        if helpershift.present:
            # present (manually) set
            initial = self.PRESENCE_PRESENT
        else:
            if helpershift.manual_presence:
                # absent manually set
                initial = self.PRESENCE_ABSENT
            else:
                # nothing manually set -> auto/unkown
                if automatic_presence:
                    initial = self.PRESENCE_AUTO
                else:
                    initial = self.PRESENCE_UNKNOWN

        super(PresenceField, self).__init__(
            widget=RadioSelect,
            choices=choices,
            initial=initial,
            disabled=disabled,
            label=helpershift.helper.full_name,
        )

    def clean(self, value):
        cleaned_value = super(PresenceField, self).clean(value)

        if cleaned_value == self.PRESENCE_PRESENT:
            return True
        if cleaned_value == self.PRESENCE_ABSENT:
            return False
        if cleaned_value == self.PRESENCE_AUTO or cleaned_value == self.PRESENCE_UNKNOWN:
            return None

    def widget_attrs(self, widget):
        return {"class": "presence"}
