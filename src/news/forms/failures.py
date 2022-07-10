from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import Person

import logging

logger = logging.getLogger("helfertool.news")


class FailuresForm(forms.Form):
    CHOICE_REMOVE = "remove"
    CHOICE_CLEAR = "clear"
    CHOICE_SKIP = "skip"
    CHOICES = [
        (CHOICE_REMOVE, _("Remove")),
        (CHOICE_CLEAR, _("Clear")),
        (CHOICE_SKIP, _("Skip")),
    ]

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop("user")

        super(FailuresForm, self).__init__(*args, **kwargs)

        for person in Person.objects.filter(mail_failed__isnull=False):
            id_str = "person_{}".format(person.pk)
            self.fields[id_str] = forms.ChoiceField(
                choices=FailuresForm.CHOICES,
                initial=FailuresForm.CHOICE_SKIP,
                widget=forms.RadioSelect,
                label=person.email,
                help_text=person.mail_failed,
            )

    def save(self):
        for person in Person.objects.filter(mail_failed__isnull=False):
            id_str = "person_{}".format(person.pk)
            action = self.cleaned_data.get(id_str)

            if action == FailuresForm.CHOICE_REMOVE:
                person.delete()

                logger.info(
                    "newsletter removed",
                    extra={
                        "user": self._user,
                        "email": person.email,
                    },
                )
            elif action == FailuresForm.CHOICE_CLEAR:
                person.mail_failed = None
                person.save()
