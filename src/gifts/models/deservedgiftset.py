from django.db import models
from django.utils.translation import ugettext_lazy as _

from .set import GiftSet


class DeservedGiftSet(models.Model):
    class Meta:
        unique_together = ('helper', 'gift_set', 'shift', )

    helper = models.ForeignKey(
        'HelpersGifts',
        on_delete=models.CASCADE,
    )

    gift_set = models.ForeignKey(
        GiftSet,
        on_delete=models.CASCADE,
    )

    delivered = models.BooleanField(
        verbose_name=_("Helper got gift"),
        default=False,
    )

    shift = models.ForeignKey(
        'registration.Shift',
        on_delete=models.CASCADE,
    )
