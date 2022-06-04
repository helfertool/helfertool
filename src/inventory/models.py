from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.utils.translation import ugettext_lazy as _

from copy import deepcopy
from datetime import datetime

from .exceptions import WrongHelper, InvalidMultipleAssignment, NotAssigned, AlreadyAssigned


class Inventory(models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    admins = models.ManyToManyField(
        get_user_model(),
        blank=True,
        verbose_name=_("Administrators of inventory"),
    )

    multiple_assignments = models.BooleanField(
        default=False,
        verbose_name=_("Same item may be assigned to different helpers"),
    )

    def __str__(self):
        return self.name

    def is_admin(self, user):
        return user.is_superuser or self.admins.filter(pk=user.pk).exists()


class Item(models.Model):
    class Meta:
        unique_together = ("inventory", "barcode")
        ordering = ["barcode"]

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    barcode = models.CharField(
        max_length=100,
        verbose_name=_("Barcode"),
    )

    comment = models.TextField(
        blank=True,
        verbose_name=_("Comment"),
    )

    def __str__(self):
        return "{} ({})".format(self.name, self.inventory.name)

    def is_available(self, event):
        if not self.inventory.multiple_assignments:
            return not self.is_in_use(event)
        return True

    def is_in_use(self, event):
        return UsedItem.objects.filter(item=self, helper__event=event, timestamp_returned=None).exists()

    def is_in_use_by_helper(self, helper):
        return UsedItem.objects.filter(item=self, helper=helper, timestamp_returned=None).exists()

    def get_exclusive_user(self, event):
        if self.inventory.multiple_assignments:
            return None

        try:
            return UsedItem.objects.get(item=self, helper__event=event, timestamp_returned=None).helper
        except UsedItem.DoesNotExist:
            raise NotAssigned
        except MultipleObjectsReturned:
            raise InvalidMultipleAssignment()

    def add_to_helper(self, helper):
        if not self.is_available(helper.event):
            raise AlreadyAssigned()

        UsedItem.objects.create(helper=helper, item=self)

    def remove_from_helper(self, helper):
        if not self.is_in_use_by_helper(helper):
            raise WrongHelper()

        uses = UsedItem.objects.filter(item=self, helper=helper, timestamp_returned=None)

        if uses.count() > 0:
            tmp = uses[0]
            tmp.timestamp_returned = datetime.now()
            tmp.save()


class UsedItem(models.Model):
    class Meta:
        ordering = ("item__inventory__name", "item__name", "timestamp")

    helper = models.ForeignKey(
        "registration.Helper",
        on_delete=models.CASCADE,
    )

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
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
        "registration.Event",
        on_delete=models.CASCADE,
    )

    available_inventory = models.ManyToManyField(
        Inventory,
        verbose_name=_("Available inventory"),
    )

    def duplicate(self, event):
        new_settings = deepcopy(self)
        new_settings.pk = None
        new_settings.event = event
        new_settings.save()

        for inventory in self.available_inventory.all():
            new_settings.available_inventory.add(inventory)

        return new_settings

    def __str__(self):
        return self.event.name
