from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

from copy import deepcopy


class GiftSettings(models.Model):
    event = models.OneToOneField(
        "registration.Event",
        on_delete=models.CASCADE,
    )

    enable_automatic_presence = models.BooleanField(
        default=False,
        verbose_name=_("Enable automatic presence for helpers"),
        help_text=_(
            "At the end of the shift, the helper is automatically set to present, " "unless the absence was reported."
        ),
    )

    default_deposit = models.IntegerField(
        verbose_name=_("Default deposit for a helper"),
        default=None,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return self.event.name

    def duplicate(self, event):
        new_settings = deepcopy(self)
        new_settings.pk = None
        new_settings.event = event

        new_settings.save()
