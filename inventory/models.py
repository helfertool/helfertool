from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from registration.models import Helper


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


class UsedItem(models.Model):
    helper = models.ForeignKey(
        Helper,
    )

    item = models.ForeignKey(
        Item,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    timestamp_returned = models.DateTimeField(
        auto_now_add=True,
    )
