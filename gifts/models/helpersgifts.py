from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .set import GiftSet
from .deservedgiftset import DeservedGiftSet


class HelpersGifts(models.Model):
    helper = models.OneToOneField(
        'registration.Helper',
        related_name = 'gifts',
    )

    deposit = models.IntegerField(
        verbose_name = _("Deposit"),
        default = None,
        null = True,
        blank = True,
        validators=[MinValueValidator(1)],
    )

    deposit_returned = models.BooleanField(
        verbose_name = _("Deposit returned"),
        default = False,
    )

    deserved_gifts = models.ManyToManyField(
        GiftSet,
        verbose_name = _("Deserved gifts"),
        blank = True,
        through = DeservedGiftSet,
    )
