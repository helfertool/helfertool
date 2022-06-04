from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from copy import deepcopy


class IncludedGift(models.Model):
    class Meta:
        unique_together = (
            "gift_set",
            "gift",
        )

    gift_set = models.ForeignKey(
        "GiftSet",
        on_delete=models.CASCADE,
    )

    gift = models.ForeignKey(
        "Gift",
        on_delete=models.CASCADE,
    )

    count = models.IntegerField(
        verbose_name=_("Count"),
        default=1,
        validators=[MinValueValidator(1)],
    )

    def duplicate(self, gift_set, gift_mapping):
        new_included = deepcopy(self)
        new_included.pk = None
        new_included.gift_set = gift_set
        new_included.gift = gift_mapping[self.gift]
        new_included.save()

        return new_included
