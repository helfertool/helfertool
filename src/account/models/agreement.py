from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_bleach.models import BleachField

import datetime


class Agreement(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    text = BleachField(
        verbose_name=_("Text"),
    )

    start = models.DateField(
        verbose_name=_("Start date"),
    )

    end = models.DateField(
        verbose_name=_("End date"),
        blank=True,
        null=True,
    )

    def clean(self):
        if self.end and self.start > self.end:
            raise ValidationError(_("End date must be after start date."))

    @property
    def in_timeframe(self):
        today = datetime.datetime.today().date()

        return self.start <= today and (self.end is None or today <= self.end)

    def __str__(self):
        return "{} ({})".format(self.name, self.start)


class UserAgreement(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    agreement = models.ForeignKey(
        Agreement,
        on_delete=models.CASCADE,
    )

    agreed = models.DateTimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return "{} - {}".format(self.agreement, self.user)
