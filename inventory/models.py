from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .exceptions import AlreadyAssigned


class Inventory(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    admins = models.ManyToManyField(
        User,
        blank=True,
        verbose_name=_("Administrators of inventory"),
    )

    multiple_assignments = models.BooleanField(
        default=False,
        verbose_name=_("Same item may be assigned to different helpers"),
    )

    def __str__(self):
        return self.name


class Item(models.Model):
    inventory = models.ForeignKey(
        Inventory,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    barcode = models.CharField(
        max_length=100,
        verbose_name=_("Barcode"),
    )

    def __str__(self):
        return "{} ({})".format(self.name, self.inventory.name)

    def add_to_helper(self, helper):
        if not self.inventory.multiple_assignments:
            other_uses = UsedItem.objects.filter(item=self,
                                                 helper__event=helper.event,
                                                 timestamp_returned=None)
            if other_uses.exists():
                raise AlreadyAssigned(other_uses[0].helper)

        UsedItem.objects.create(helper=helper, item=self)

    def is_available(self, event):
        if not self.inventory.multiple_assignments:
            return not UsedItem.objects.filter(item=self, helper__event=event,
                                               timestamp_returned=None) \
                                       .exists()
        return True


class UsedItem(models.Model):
    helper = models.ForeignKey(
        'registration.Helper',
    )

    item = models.ForeignKey(
        Item,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    timestamp_returned = models.DateTimeField(
        null=True,
        blank=True,
    )


class InventorySettings(models.Model):
    event = models.OneToOneField(
        'registration.Event'
    )

    available_inventory = models.ManyToManyField(
        Inventory,
        verbose_name=_("Available inventory"),
    )

    def __str__(self):
        return self.event.name
