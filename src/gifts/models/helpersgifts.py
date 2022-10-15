from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from registration.models.helpershift import HelperShift

from .set import GiftSet
from .deservedgiftset import DeservedGiftSet

from collections import OrderedDict


class HelpersGifts(models.Model):
    """
    Important: if new fields are added here, they need to be handled in HelpersGiftsForm.
    The gift-related fields can be switched to read-only, so they need to be added there.
    """

    helper = models.OneToOneField(
        "registration.Helper",
        related_name="gifts",
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
        - update shifts to present, if the end was in the past.
        - sync DeservedGiftSet with real shifts (so for every shift, there must be a DeservedGiftSet)

        :return: None
        """
        cur_gifts = DeservedGiftSet.objects.filter(helper=self)
        shifts_delete = [(g.shift, g.gift_set) for g in cur_gifts.all()]
        shifts_new = []

        for helpershift in HelperShift.objects.filter(helper=self.helper):
            shift = helpershift.shift

            # update presence automatically
            if self.helper.event.gift_settings.enable_automatic_presence and self._check_auto_presence(helpershift):
                # shift has ended in the past -> set present
                helpershift.present = True
                helpershift.manual_presence = False
                helpershift.save()

            # find changes for sync of DeservedGiftSet and shifts
            for gift in shift.gifts.all():
                tmp = DeservedGiftSet.objects.filter(helper=self, gift_set=gift, shift=shift)

                if tmp.exists():
                    shifts_delete.remove((shift, gift))
                else:
                    shifts_new.append((shift, gift))

        # apply the changes of DeservedGiftSets
        for delete in shifts_delete:
            DeservedGiftSet.objects.filter(helper=self, shift=delete[0], gift_set=delete[1]).delete()

        for new in shifts_new:
            DeservedGiftSet.objects.create(helper=self, shift=new[0], gift_set=new[1])

    def gifts_sum(self):
        """
        Returns the sum of all deserved gifts (gifts where the helper was marked
        present.
        :return dict {"<giftname>" : {'total': <int>, 'given': <int>, 'earned': <int>,
                                      'pending_with_deposit': <int>, 'pending': <int>} }
        """
        result = OrderedDict()
        default_fields = {
            "total": 0,
            "given": 0,
            "earned": 0,
            "pending": 0,
            "pending_with_deposit": 0,
        }
        # iterate over all deserved gifts of this helper
        for deserved_gift in DeservedGiftSet.objects.filter(helper=self):
            gift_set = deserved_gift.gift_set

            # we need to know whether the helper was present or not
            helpershift = HelperShift.objects.get(helper=self.helper, shift=deserved_gift.shift)
            present_at_shift = helpershift.present
            present_pending = not helpershift.manual_presence

            already_delivered = deserved_gift.delivered

            # not iterate over all gifts inside the deserved gift set
            for included_gift in gift_set.includedgift_set.all():
                name = included_gift.gift.name
                count = included_gift.count

                data = result.setdefault(name, default_fields.copy())

                # as long as the helper is not absent, count the gifts
                if present_at_shift or present_pending:
                    data["total"] += count

                if already_delivered:
                    # gift was delivered
                    data["given"] += count

                elif present_at_shift or present_pending:
                    # helper can receive this gift, if he pays deposit
                    data["pending_with_deposit"] += count

                if present_at_shift:
                    # if the helper was marked as present, he earned it
                    data["earned"] += count

                    if not already_delivered:
                        # helper can receive this gift
                        data["pending"] += count

        return result

    def set_present(self, shift, present):
        """
        Uptate presence in HelperShift
        :param shift: The shift
        :param present: True, False or None. None means that automatic presence is used.
        :return: None
        """
        try:
            helpershift = HelperShift.objects.get(helper=self.helper, shift=shift)

            if present is None:
                # None -> automatic presence
                helpershift.manual_presence = False
                helpershift.present = self._check_auto_presence(helpershift)
                helpershift.save()
            else:
                # presence manually set
                helpershift.manual_presence = True
                helpershift.present = present
                helpershift.save()
        except HelperShift.DoesNotExist:
            pass

    def _check_auto_presence(self, helpershift):
        """
        Check if present flag should be set to True or False based on automatic presence.
        """
        if self.helper.event.gift_settings.enable_automatic_presence and not helpershift.manual_presence:
            return timezone.now() > helpershift.shift.end
        return False

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
            own_deservedgiftset = DeservedGiftSet.objects.filter(helper=self, gift_set=gift.gift_set, shift=gift.shift)

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
