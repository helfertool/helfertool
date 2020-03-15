from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from collections import OrderedDict

from .set import GiftSet
from .deservedgiftset import DeservedGiftSet
from registration.models.helpershift import HelperShift


class HelpersGifts(models.Model):
    helper = models.OneToOneField(
        'registration.Helper',
        related_name='gifts',
        on_delete=models.CASCADE,
    )

    deposit = models.IntegerField(
        verbose_name=_("Deposit"),
        default=None,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )

    deposit_returned = models.BooleanField(
        verbose_name=_("Deposit returned"),
        default=False,
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
        verbose_name=_("Deserved gifts"),
        blank=True,
        through=DeservedGiftSet,
    )

    @transaction.atomic
    def update(self):
        """
        Update the consistency of the database:
        - remove deservedgifts if the helper is not present
        - add deservedgifts if the helper is present
        - update shifts to present, if the end was in the past.

        :return: None
        """
        # TODO: race conditions possible?
        cur_gifts = DeservedGiftSet.objects.filter(helper=self)
        shifts_delete = [(g.shift, g.gift_set) for g in cur_gifts.all()]
        shifts_new = []

        for helpershift in self.helper.helpershift_set.all():
            shift = helpershift.shift

            if self.helper.event.gift_settings \
                and self.helper.event.gift_settings.enable_automatic_availability\
                and not helpershift.manual_presence\
                and timezone.now() > shift.end:
                # shift has ended in the past
                helpershift.present = True
                helpershift.manual_presence = False
                helpershift.save()

            for gift in shift.gifts.all():
                tmp = DeservedGiftSet.objects.filter(helper=self,
                                                     gift_set=gift,
                                                     shift=shift)

                if tmp.exists() and helpershift.present:
                    shifts_delete.remove((shift, gift))
                elif helpershift.present:
                    shifts_new.append((shift, gift))
                else:
                    # 1) the helper is new and not marked as present yet.
                    # 2) the helper has previously earned the gift, but is now marked
                    #    as absent -> delete this deserved gift
                    pass

        for delete in shifts_delete:
            DeservedGiftSet.objects.filter(helper=self, shift=delete[0],
                                           gift_set=delete[1]).delete()

        for new in shifts_new:
            DeservedGiftSet.objects.create(helper=self, shift=new[0],
                                           gift_set=new[1])

    def gifts_sum(self):
        """
        Returns the sum of all deserved gifts (gifts where the helper was marked
        present.
        :return dict {<giftname> : {'given': <int>, 'total': <int>, 'missing':<int>} }
        """
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

        for name in result.keys():
            result[name]['missing'] = result[name]['total'] - result[name]['given']

        return result

    def get_present(self, shift):
        helpershift = self.helper.helpershift_set.filter(shift=shift).values_list(named=True)
        return helpershift.exists() and helpershift[0].present

    def set_present(self, shift, present):
        """
        TODO: Uptate deservedgiftset
        :param shift:
        :param present:
        :return:
        """
        helpershift = HelperShift.objects.filter(helper=self.helper, shift=shift)

        if present is None:
            helpershift.update(manual_presence=False)
            helpershift.update(present=timezone.now() > shift.end)
            return

        helpershift.update(manual_presence=True)
        helpershift.update(present=present)

    def merge(self, other_gifts):
        # handle not returned deposit
        if other_gifts.deposit:
            # both have same state -> add
            if self.deposit_returned == other_gifts.deposit_returned:
                self.deposit = (self.deposit or 0) + other_gifts.deposit
            # other not returned -> overwrite own deposit
            elif self.deposit_returned and not other_gifts.deposit_returned:
                self.deposit = other_gifts.deposit
                self.deposit_returned = False

        # shirt flags
        if other_gifts.got_shirt:
            self.got_shirt = True

        if other_gifts.buy_shirt:
            self.buy_shirt = True

        # deserved gifts
        for gift in DeservedGiftSet.objects.filter(helper=other_gifts):
            # check if it exists for this helper and the same gift_set and
            # shift already
            own_deservedgiftset = DeservedGiftSet.objects.filter(
                helper=self,
                gift_set=gift.gift_set,
                shift=gift.shift)

            if own_deservedgiftset.exists():
                # update "delivered" flag, delete other
                own_obj = own_deservedgiftset.get()

                if gift.delivered:
                    own_obj.delivered = True
                    own_obj.save()

                gift.delete()
            else:
                # keep object, update foreign key
                gift.helper = self
                gift.save()

        self.save()
