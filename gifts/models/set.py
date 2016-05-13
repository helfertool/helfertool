from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .gift import Gift


@python_2_unicode_compatible
class GiftSet(models.Model):
    name = models.EmailField(
        verbose_name=_("Name"),
    )

    gifts = models.ManyToManyField(
        Gift,
        verbose_name=_("Gifts"),
    )

    def __str__(self):
        return self.name
