from django.db import models
from django.utils.translation import ugettext_lazy as _


class GiftSettings(models.Model):
    event = models.OneToOneField(
        'registration.Event',
        on_delete=models.CASCADE,
    )

    enable_automatic_availability = models.BooleanField(
        default=False,
        verbose_name=_("Enable automatic availability confirmation at the end "
                       "of a shift if absence was not reported")
    )

    default_deposit = models.IntegerField(
        verbose_name=_("Default Deposit for a helper shift"),
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.event.name
