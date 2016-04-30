from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

@python_2_unicode_compatible
class Gift(models.Model):
    name = models.EmailField(
        verbose_name=_("Name"),
    )

    def __str__(self):
        return self.name
