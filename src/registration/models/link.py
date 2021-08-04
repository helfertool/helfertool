from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

import uuid


class Link(models.Model):
    """ Link to some shifts for registration

    Columns:
        :id: Primary key, UUID
        :event: The event
        :shifts: Shifts that are linked
        :creator: User that created the link
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
    )

    shifts = models.ManyToManyField(
        'Shift',
    )

    creator = models.ForeignKey(
        get_user_model(),
        null=True,
        on_delete=models.SET_NULL,
    )

    usage = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Usage"),
    )
