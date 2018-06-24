from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_bleach.models import BleachField


class AbstractSetting(models.Model):
    """
    All types of settings have a key
    """
    class Meta:
        abstract = True

    key = models.CharField(
        max_length=200,
        unique=True,
        validators=[RegexValidator('^[a-zA-Z0-9]+$')],
        verbose_name=_("Key"),
    )

    def __str__(self):
        return self.key


class HTMLSetting(AbstractSetting):
    value = BleachField(
        blank=True,
        default="",
        verbose_name=_("HTML"),
    )


class TextSetting(AbstractSetting):
    value = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Text"),
    )
