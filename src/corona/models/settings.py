from django.db import models
from django.utils.translation import ugettext_lazy as _

from copy import deepcopy


class CoronaSettings(models.Model):
    RULES_2G = '2G'
    RULES_3G = '3G'
    RULES_3Gplus = '3Gplus'

    RULES_CHOICES = (
        (RULES_2G, _("2G")),
        (RULES_3G, _("3G")),
        (RULES_3Gplus, _("3G plus")),
    )

    event = models.OneToOneField(
        'registration.Event',
        on_delete=models.CASCADE,
    )

    rules = models.CharField(
        choices=RULES_CHOICES,
        default=RULES_2G,
        max_length=20,
        verbose_name=_("Admission rules"),
    )

    def duplicate(self, event):
        new_settings = deepcopy(self)
        new_settings.pk = None
        new_settings.event = event
        new_settings.save()

        return new_settings

    def __str__(self):
        return self.event.name
