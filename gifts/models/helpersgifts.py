from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from collections import OrderedDict

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

    got_shirt = models.BooleanField(
        default=False,
        verbose_name=_("Helper got her T-shirt"),
    )

    buy_shirt = models.BooleanField(
        default=False,
        verbose_name=_("Buy a T-shirt for helper"),
    )

    deserved_gifts = models.ManyToManyField(
        GiftSet,
        verbose_name = _("Deserved gifts"),
        blank = True,
        through = DeservedGiftSet,
    )

    def update(self):
        # TODO: race conditions possible?

        cur_gifts = DeservedGiftSet.objects.filter(helper=self)
        shifts_delete = [(g.shift, g.gift_set) for g in cur_gifts.all()]
        shifts_new = []

        for shift in self.helper.shifts.all():
            for gift in shift.gifts.all():
                tmp = DeservedGiftSet.objects.filter(helper=self,
                                                     gift_set=gift,
                                                     shift=shift)

                if tmp.exists():
                    shifts_delete.remove((shift, gift))
                else:
                    shifts_new.append((shift, gift))

        for delete in shifts_delete:
            DeservedGiftSet.objects.filter(helper=self, shift=delete[0],
                                           gift_set=delete[1]).delete()

        for new in shifts_new:
            DeservedGiftSet.objects.create(helper=self, shift=new[0],
                                           gift_set=new[1])

    def gifts_sum(self):
        result = OrderedDict()

        deserved_gift_sets = DeservedGiftSet.objects.filter(helper=self)

        # TODO: maybe do one query for this?
        for deserved_gift in deserved_gift_sets:
            gift_set = deserved_gift.gift_set

            for included_gift in gift_set.includedgift_set.all():
                name = included_gift.gift.name
                if name not in result:
                    result[name] = {'given': 0, 'total': 0}

                result[name]['total'] += included_gift.count
                if deserved_gift.delivered:
                    result[name]['given'] += included_gift.count

        return result
