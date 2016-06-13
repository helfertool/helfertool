from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .gift import Gift
from .includedgift import IncludedGift


@python_2_unicode_compatible
class GiftSet(models.Model):
    name = models.CharField(
        max_length = 200,
        verbose_name=_("Name"),
    )

    gifts = models.ManyToManyField(
        Gift,
        verbose_name=_("Gifts"),
        through = IncludedGift,
    )

    event = models.ForeignKey(
        'registration.Event',
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.name

    def get_gift_num(self, gift):
        try:
            tmp = IncludedGift.objects.get(gift_set=self, gift=gift)
            return tmp.count
        except (IncludedGift.DoesNotExist, MultipleObjectsReturned):
            return 0

    def set_gift_num(self, gift, num):
        try:
            tmp = IncludedGift.objects.get(gift_set=self, gift=gift)

            if num == 0:
                tmp.delete()
            else:
                tmp.count = num
                tmp.save()
        except IncludedGift.DoesNotExist:
            if num:
                IncludedGift.objects.create(gift_set=self, gift=gift,
                                            count=num)
