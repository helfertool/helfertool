from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from registration.models import Event


@python_2_unicode_compatible
class Gift(models.Model):
    name = models.CharField(
        max_length = 200,
        verbose_name=_("Name"),
    )

    event = models.ForeignKey(
        Event,
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.name
