from django.db import models
from django.utils.translation import gettext_lazy as _

from .event import Event


class EventArchive(models.Model):
    """
    Data store for archived events. This is meant for statistics or similar data that is based on helper data.

    Note: The number of registered helpers are not stored in this table, but directly in the shifts.

    Columns:
        :event: the event to which this data belongs
        :key: key to identify the data (e.g. "shirts")
        :version: in case the data format changes the version can be incremented (default: 1)
        :data: JSON data
    """

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
    )

    key = models.CharField(
        max_length=200,
        verbose_name=_("Key"),
    )

    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Version"),
    )

    data = models.JSONField(
        verbose_name=_("Data"),
    )

    def __str__(self):
        return "{} - {}".format(self.event, self.key)
