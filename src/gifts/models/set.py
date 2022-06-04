from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .gift import Gift
from .includedgift import IncludedGift

from copy import deepcopy


class GiftSet(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    gifts = models.ManyToManyField(
        Gift,
        verbose_name=_("Gifts"),
        through=IncludedGift,
    )

    event = models.ForeignKey(
        "registration.Event",
        on_delete=models.CASCADE,
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
                IncludedGift.objects.create(gift_set=self, gift=gift, count=num)

    def duplicate(self, event, gift_mapping):
        new_gift_set = deepcopy(self)
        new_gift_set.pk = None
        new_gift_set.event = event
        new_gift_set.save()

        # copy m2m field gifts
        for included in IncludedGift.objects.filter(gift_set=self):
            included.duplicate(new_gift_set, gift_mapping)

        return new_gift_set
