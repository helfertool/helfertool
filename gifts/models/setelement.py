from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class GiftSetElement(models.Model):
    gift_set = models.ForeignKey(
        'GiftSet',
        on_delete = models.CASCADE,
    )

    gift = models.ForeignKey(
        'Gift',
        on_delete = models.CASCADE,
    )

    count = models.IntegerField(
        verbose_name = _("Count"),
        default = 1,
        validators=[MinValueValidator(1)],
    )
