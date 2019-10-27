from django.db import models
from django.utils.translation import ugettext_lazy as _

import uuid


class Person(models.Model):
    class Meta:
        ordering = ['timestamp', ]

    token = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        verbose_name=_("E-Mail"),
        unique=True,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    withevent = models.BooleanField(
        default=True,
        verbose_name=_("Helper subscribed during registration for event"),
    )

    def __str__(self):
        return self.email
