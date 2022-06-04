from django.db import models

import uuid

from .helper import Helper


class Duplicate(models.Model):
    """Duplicated helper that was deleted.

    The mapping from old to new UUID is used so that the "registered" and
    "validate" URLs in the mail are still working.
    """

    deleted = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )

    existing = models.ForeignKey(
        Helper,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "%s %s" % (self.existing.firstname, self.existing.surname)
