from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

@python_2_unicode_compatible
class Person(models.Model):
    email = models.EmailField(
        verbose_name=_("E-Mail"),
        unique=True,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.email
