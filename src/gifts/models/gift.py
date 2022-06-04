from django.db import models
from django.utils.translation import ugettext_lazy as _

from copy import deepcopy


class Gift(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    event = models.ForeignKey(
        "registration.Event",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    def duplicate(self, event):
        new_gift = deepcopy(self)
        new_gift.pk = None
        new_gift.event = event
        new_gift.save()

        return new_gift
