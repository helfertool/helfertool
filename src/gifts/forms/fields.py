from django.forms import ChoiceField, RadioSelect
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import lazy

from django_icons import icon


def choice(icon_name, classes, text):
    return mark_safe(format_lazy('<span class="{classes}"> {icon} {text}</span>',
                                 icon=icon(icon_name), classes=classes, text=text))


choice_lazy = lazy(choice)


class PresenceField(ChoiceField):
    """
    This field gets a HelperShift as input and returns the presence status as True/False/None:

    * True: the helper was present
    * False: the helper was absent
    * None: Auto was selected
    """

    PRESENCE_AUTO = "auto"
    PRESENCE_PRESENT = "present"
    PRESENCE_ABSENT = "absent"

    PRESENCE_CHOICES_AUTO = [
        (PRESENCE_AUTO, choice_lazy("clock", "text-info", _("Auto"))),
    ]

    PRESENCE_CHOICES = [
        (PRESENCE_PRESENT, choice_lazy("check", "text-success", _("Present"))),
        (PRESENCE_ABSENT, choice_lazy("times", "text-danger", _("Absent"))),
    ]

    def __init__(self, *args, **kwargs):
        automatic_availability = kwargs.pop("automatic_availability")
        helpershift = kwargs.pop("helpershift")

        # depending on the automatic availability setting, add "auto"
        if automatic_availability:
            choices = self.PRESENCE_CHOICES_AUTO + self.PRESENCE_CHOICES
        else:
            choices = self.PRESENCE_CHOICES

        # initial value
        if helpershift.present:
            initial = self.PRESENCE_PRESENT
        else:
            if helpershift.manual_presence:
                initial = self.PRESENCE_ABSENT
            else:
                initial = self.PRESENCE_AUTO

        super(PresenceField, self).__init__(
            widget=RadioSelect,
            choices=choices,
            initial=initial,
            label=helpershift.helper.full_name,
        )

    def clean(self, value):
        cleaned_value = super(PresenceField, self).clean(value)

        if cleaned_value == self.PRESENCE_PRESENT:
            return True
        if cleaned_value == self.PRESENCE_ABSENT:
            return False
        if cleaned_value == self.PRESENCE_AUTO:
            return None

    def widget_attrs(self, widget):
        return {"class": "list-inline presence"}
